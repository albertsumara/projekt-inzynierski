class MockImageClassifier:
    def __init__(self):
        self.calls = []

    def recognize(self, image):
        self.calls.append(image)
        return [{"id_ml": 7, "confidence": 0.95}]
