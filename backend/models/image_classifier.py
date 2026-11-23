import json
import os

import dotenv
import numpy as np
from paths import (
    ENV_CONFIGURATION_PATH,
    IMAGENET_FOOD_CLASSES_PATH,
    MODEL_PATH,
)
from PIL import Image

dotenv.load_dotenv(ENV_CONFIGURATION_PATH)


class ImageClassifier:
    def __init__(self) -> None:
        self._model = None
        self._preprocess_input = None
        self._imagenet_food_class_ids: tuple[int, ...] = ()
        self._custom_classes_offset = int(os.getenv("CUSTOM_CLASSES_ID_OFFSET", "1000"))

    def _load_model(self) -> None:
        if self._model is not None:
            return

        import tensorflow as tf
        from tensorflow.keras.applications.mobilenet_v2 import preprocess_input  # type: ignore[reportMissingImports]

        with IMAGENET_FOOD_CLASSES_PATH.open("r", encoding="utf-8") as classes_file:
            self._imagenet_food_class_ids = tuple(
                sorted(int(class_id) for class_id in json.load(classes_file))
            )

        self._model = tf.keras.models.load_model(
            MODEL_PATH,
            compile=False,
        )

        self._preprocess_input = preprocess_input

    def _prepare_image(self, image):
        resized_image = image.convert("RGB").resize((224, 224))
        image_array = np.asarray(resized_image, dtype=np.float32)
        image_array = np.expand_dims(image_array, axis=0)
        if self._preprocess_input is None:
            raise RuntimeError("Model preprocessing has not been loaded.")
        image_array = self._preprocess_input(image_array)
        return image_array

    def _recognize_imagenet_classes(
        self,
        scores: np.ndarray,
    ) -> list[dict[str, int | float]]:
        return [
            {
                "id_ml": class_id,
                "confidence": round(float(scores[class_id]), 4),
            }
            for class_id in self._imagenet_food_class_ids
            if class_id < len(scores)
        ]

    def _recognize_custom_classes(
        self,
        scores: np.ndarray,
    ) -> list[dict[str, int | float]]:
        return [
            {
                "id_ml": output_index + self._custom_classes_offset,
                "confidence": round(float(score), 4),
            }
            for output_index, score in enumerate(scores)
        ]

    def recognize(self, image: Image.Image) -> list[dict[str, int | float]]:
        self._load_model()

        image_array = self._prepare_image(image)

        if self._model is None:
            raise RuntimeError("Model preprocessing has not been loaded.")
        imagenet_probabilities, custom_probabilities = self._model.predict(
            image_array,
            verbose=0,
        )

        results = self._recognize_imagenet_classes(imagenet_probabilities[0])
        results.extend(self._recognize_custom_classes(custom_probabilities[0]))
        return sorted(
            results,
            key=lambda result: result["confidence"],
            reverse=True,
        )[:3]
