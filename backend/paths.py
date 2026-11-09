from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

MACHINE_LEARNING_DIR = BASE_DIR / "machine_learning"
ENV_CONFIGURATION_PATH = BASE_DIR / ".env"
OUTPUT_DIR = BASE_DIR / "trained"

DATASET_DIR = MACHINE_LEARNING_DIR / "dataset"
RAW_DIR = DATASET_DIR / "raw"
TRAIN_DIR = DATASET_DIR / "train"
VALIDATION_DIR = DATASET_DIR / "validation"

LOG_DIR = MACHINE_LEARNING_DIR / "logs"
TRAINED_DIR = MACHINE_LEARNING_DIR / "trained"
MACHINE_LEARNING_CONFIG_DIR = MACHINE_LEARNING_DIR / "config"

MODEL_PATH = TRAINED_DIR / "product_classifier.keras"
CLASSES_PATH = TRAINED_DIR / "classes.json"

IMAGENET_FOOD_CLASSES = MACHINE_LEARNING_CONFIG_DIR / "imagenet_food_classes.json"
