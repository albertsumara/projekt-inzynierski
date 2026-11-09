import json

import numpy as np
from paths import CLASSES_PATH, IMAGENET_FOOD_CLASSES, MODEL_PATH
from PIL import Image


class ImageClassifier:
    def __init__(self) -> None:
        self._model = None
        self._custom_classes = None
        self._imagenet_classes = None
        self._decode_recognitions = None
        self._preprocess_input = None
        # this offset is used because indexes 0...999 are used by imagenet set
        self.CUSTOM_ID_OFFSET = 1000

    def _load_model(self) -> None:
        if self._model is not None:
            return

        import tensorflow as tf
        from tensorflow.keras.applications.mobilenet_v2 import (
            decode_predictions,
            preprocess_input,
        )

        self._model = tf.keras.models.load_model(
            MODEL_PATH,
            compile=False,
        )

        with open(
            IMAGENET_FOOD_CLASSES, "r", encoding="utf-8"
        ) as imagenet_classes_file:
            raw_imagenet_classes = json.load(imagenet_classes_file)
            self._imagenet_classes = {
                int(k): v for k, v in raw_imagenet_classes.items()
            }

        with open(CLASSES_PATH, "r", encoding="utf-8") as file:
            raw_custom_classes = json.load(file)
            self._custom_classes = {
                index + self.CUSTOM_ID_OFFSET: product_name
                for index, product_name in enumerate(raw_custom_classes)
            }

        self._decode_recognitions = decode_predictions
        self._preprocess_input = preprocess_input

    def _prepare_image(self, image):
        resized_image = image.convert("RGB").resize((224, 224))
        image_array = np.asarray(resized_image, dtype=np.float32)
        image_array = np.expand_dims(image_array, axis=0)
        image_array = self._preprocess_input(image_array)
        return image_array

    def recognize(self, image: Image.Image) -> list[dict]:
        self._load_model()

        image_array = self._prepare_image(image)

        imagenet_probabilities, custom_probabilities = self._model.predict(
            image_array,
            verbose=0,
        )

        results = []
        imagenet_scores = imagenet_probabilities[0]

        for imagenet_class_index, product_label in self._imagenet_classes.items():
            if imagenet_class_index < len(imagenet_scores):
                results.append(
                    {
                        "class_id": str(imagenet_class_index),
                        "product": product_label,
                        "confidence": round(
                            float(imagenet_scores[imagenet_class_index]), 4
                        ),
                    }
                )

        custom_scores = custom_probabilities[0]

        for custom_class_index, product_label in self._custom_classes.items():
            results.append(
                {
                    "class_id": str(custom_class_index),
                    "product": product_label,
                    "confidence": round(
                        float(
                            custom_scores[custom_class_index - self.CUSTOM_ID_OFFSET]
                        ),
                        4,
                    ),
                }
            )

        results.sort(
            key=lambda result: result["confidence"],
            reverse=True,
        )
        return results[:3]
