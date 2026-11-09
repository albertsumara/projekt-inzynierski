from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

MACHINE_LEARNING_DIR = BASE_DIR / "machine_learning"

OUTPUT_DIR = BASE_DIR / "trained"
DATASET_DIR = MACHINE_LEARNING_DIR / "dataset"
RAW_DIR = DATASET_DIR / "raw"
TRAIN_DIR = DATASET_DIR / "train"
VALIDATION_DIR = DATASET_DIR / "validation"

TRAINED_DIR = MACHINE_LEARNING_DIR / "trained"
MODEL_PATH = TRAINED_DIR / "product_classifier.keras"
CLASSES_PATH = TRAINED_DIR / "classes.json"

LOG_DIR = MACHINE_LEARNING_DIR / "logs"

MACHINE_LEARNING_CONFIG_DIR = MACHINE_LEARNING_DIR / "config"
IMAGENET_FOOD_CLASSES = MACHINE_LEARNING_CONFIG_DIR / "imagenet_food_classes.json"
