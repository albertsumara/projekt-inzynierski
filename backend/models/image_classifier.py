import json

import numpy as np
from paths import CLASSES_PATH, MODEL_PATH
from PIL import Image


class ImageClassifier:
    def __init__(self) -> None:
        self._model = None
        self._classes = None
        self._decode_recognitions = None
        self._preprocess_input = None

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

        with open(CLASSES_PATH, "r", encoding="utf-8") as file:
            self._classes = json.load(file)

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

        imagenet_results = self._decode_recognitions(
            imagenet_probabilities,
            top=3,
        )[0]

        results = [
            {
                "class_id": class_id,
                "product": label,
                "confidence": round(float(score), 4),
            }
            for class_id, label, score in imagenet_results
        ]

        custom_scores = custom_probabilities[0]
        custom_top_indices = np.argsort(custom_scores)[-3:][::-1]

        for index in custom_top_indices:
            results.append(
                {
                    "class_id": f"custom_{self._classes[index]}",
                    "product": self._classes[index],
                    "confidence": round(float(custom_scores[index]), 4),
                }
            )

        results.sort(
            key=lambda result: result["confidence"],
            reverse=True,
        )
        return results[:3]
