import numpy as np
from PIL import Image


class ImageClassifier:
    def __init__(self) -> None:
        self._model = None
        self._decode_recognitions = None
        self._preprocess_input = None

    def _load_model(self) -> None:
        if self._model is not None:
            return

        from tensorflow.keras.applications import MobileNetV2
        from tensorflow.keras.applications.mobilenet_v2 import (
            decode_predictions,
            preprocess_input,
        )

        self._model = MobileNetV2(weights="imagenet")
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

        probabilities = self._model.predict(
            image_array,
            verbose=0,
        )

        results = self._decode_recognitions(
            probabilities,
            top=3,
        )[0]

        return [
            {
                "class_id": class_id,
                "product": label,
                "confidence": round(float(score), 4),
            }
            for class_id, label, score in results
        ]
