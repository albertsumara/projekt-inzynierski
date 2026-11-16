import json
import os

import tensorflow as tf
from dotenv import load_dotenv
from paths import (
    CUSTOM_FOOD_CLASSES_PATH,
    CUSTOM_FOOD_INGREDIENTS,
    INGREDIENTS_DIR,
    LOG_DIR,
    MODEL_PATH,
    OUTPUT_DIR,
    TRAIN_DIR,
    VALIDATION_DIR,
)
from tensorflow.keras import Model, layers
from tensorflow.keras.applications import MobileNetV2

load_dotenv()
CUSTOM_CLASSES_ID_OFFSET = int(os.getenv("CUSTOM_CLASSES_ID_OFFSET", "1000"))
IMAGE_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 15
SEED = 42


def train_model():

    _create_dirs()

    # loads training dataset and assigns class labels
    train_ds = tf.keras.utils.image_dataset_from_directory(
        TRAIN_DIR,
        image_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        label_mode="int",
        seed=SEED,
    )

    class_names = train_ds.class_names

    class_map, ingredients_map = prepare_new_custom_classes_data(class_names)

    # loads validation dataset
    validation_ds = tf.keras.utils.image_dataset_from_directory(
        VALIDATION_DIR,
        image_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        label_mode="int",
        class_names=class_names,
        seed=SEED,
        shuffle=False,
    )

    # random modifications
    augmentation = tf.keras.Sequential(
        [
            layers.RandomFlip("horizontal"),
            layers.RandomRotation(0.08),
            layers.RandomZoom(0.1),
        ]
    )

    # imagenet set loaded from MobileNetV2
    imagenet_model = MobileNetV2(
        weights="imagenet",
        include_top=True,
        input_shape=(224, 224, 3),
    )

    # disable changing already trained imagenet values
    imagenet_model.trainable = False

    # extractor that returns ImageNet predictions
    feature_extractor = Model(
        inputs=imagenet_model.input,
        outputs=[imagenet_model.output, imagenet_model.layers[-2].output],
        name="mobilenet_feature_extractor",
    )

    # custom layer that classifies products
    product_head = layers.Dense(
        len(class_names),
        activation="softmax",
        name="product_predictions",
    )

    inputs = layers.Input(shape=(224, 224, 3))

    # pixel augmentatation and normalization (data scaling)
    x = augmentation(inputs)
    x = layers.Rescaling(
        scale=1.0 / 127.5,
        offset=-1,
    )(x)

    _, features = feature_extractor(x)

    outputs = product_head(features)

    # model designed for training
    training_model = Model(
        inputs=inputs,
        outputs=outputs,
        name="product_training_model",
    )

    # optimizer, loss, and metric
    training_model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss="sparse_categorical_crossentropy",
        metrics=[
            "accuracy",
        ],
    )

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_loss",
            patience=4,
            restore_best_weights=True,
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=2,
            min_lr=0.00001,
        ),
        tf.keras.callbacks.CSVLogger(LOG_DIR / "training_history.csv"),
        tf.keras.callbacks.TensorBoard(log_dir=LOG_DIR / "tensorboard"),
    ]

    training_model.fit(
        train_ds,
        validation_data=validation_ds,
        epochs=EPOCHS,
        callbacks=callbacks,
    )

    imagenet_output, features = feature_extractor(
        imagenet_model.input,
    )

    product_output = product_head(features)

    combined_model = Model(
        inputs=imagenet_model.input,
        outputs=[imagenet_output, product_output],
        name="product_classifier",
    )

    combined_model.save(MODEL_PATH)

    with open(CUSTOM_FOOD_CLASSES_PATH, "w", encoding="utf-8") as classes_file:
        json.dump(class_map, classes_file, ensure_ascii=False, indent=4)

    with open(CUSTOM_FOOD_INGREDIENTS, "w", encoding="utf-8") as ingredients_file:
        json.dump(ingredients_map, ingredients_file, ensure_ascii=False, indent=4)


def prepare_new_custom_classes_data(new_class_names):
    if CUSTOM_FOOD_CLASSES_PATH.exists():
        with open(CUSTOM_FOOD_CLASSES_PATH, "r", encoding="utf-8") as file:
            class_map_existed = json.load(file)
    else:
        class_map_existed = {}
    new_class_map = {}
    ingredients_map = {}
    classes_not_existed = []
    for class_name in new_class_names:
        if class_name in class_map_existed.values():
            idx = next(
                (
                    key
                    for key, value in class_map_existed.items()
                    if value == class_name
                ),
                None,
            )
            new_class_map[idx] = class_name
            ingredients_map[idx] = _load_ingredients_data(class_name)
            continue
        classes_not_existed.append(class_name)
    next_id = (
        max(map(int, class_map_existed.keys()), default=CUSTOM_CLASSES_ID_OFFSET - 1)
        + 1
    )
    for class_name in classes_not_existed:
        new_class_map[str(next_id)] = class_name
        ingredients_map[next_id] = _load_ingredients_data(class_name)
        next_id += 1
    return new_class_map, ingredients_map


def _load_ingredients_data(class_name):
    with open(
        f"{INGREDIENTS_DIR}/{class_name}.json", "r", encoding="utf-8"
    ) as ingredient_file:
        return json.load(ingredient_file)


def _create_dirs():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    CUSTOM_FOOD_CLASSES_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    train_model()
