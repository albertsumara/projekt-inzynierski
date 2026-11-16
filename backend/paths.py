from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

MACHINE_LEARNING_DIR = BASE_DIR / "machine_learning"
ENV_CONFIGURATION_PATH = BASE_DIR / ".env"
OUTPUT_DIR = BASE_DIR / "trained"

DATA_DIR = BASE_DIR / "data"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
IMAGENET_FOOD_CLASSES_PATH = PROCESSED_DATA_DIR / "imagenet_food_classes.json"
CUSTOM_FOOD_CLASSES_PATH = PROCESSED_DATA_DIR / "custom_classes.json"
IMAGENET_FOOD_INGREDIENTS = PROCESSED_DATA_DIR / "imagenet_ingredients.json"
CUSTOM_FOOD_INGREDIENTS = PROCESSED_DATA_DIR / "custom_ingredients.json"


DATASET_DIR = MACHINE_LEARNING_DIR / "dataset"
RAW_DIR = DATASET_DIR / "raw"
TRAIN_DIR = DATASET_DIR / "train"
VALIDATION_DIR = DATASET_DIR / "validation"
INGREDIENTS_DIR = DATASET_DIR / "ingridients"

LOG_DIR = MACHINE_LEARNING_DIR / "logs"
TRAINED_DIR = MACHINE_LEARNING_DIR / "trained"

MODEL_PATH = TRAINED_DIR / "product_classifier.keras"
