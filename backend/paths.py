from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

MACHINE_LEARNING_DIR = BASE_DIR / "machine_learning"
ENV_CONFIGURATION_PATH = BASE_DIR / ".env"
ENV_TEST_CONFIGURATION_PATH = BASE_DIR / ".env.test"
OUTPUT_DIR = BASE_DIR / "trained"

DATA_DIR = BASE_DIR / "data"
RECIPES_DATA_DIR = DATA_DIR / "recipes"
USERS_DATA_DIR = DATA_DIR / "users"
CUSTOM_PRODUCTS_DATA_DIR = DATA_DIR / "custom_products"
IMAGENET_PRODUCTS_DATA_DIR = DATA_DIR / "imagenet_products"

IMAGENET_FOOD_CLASSES_PATH = IMAGENET_PRODUCTS_DATA_DIR / "imagenet_food_classes.json"
IMAGENET_FOOD_INGREDIENTS_PATH = (
    IMAGENET_PRODUCTS_DATA_DIR / "imagenet_ingredients.json"
)
IMAGENET_PRODUCT_MEASUREMENT_TYPES_PATH = (
    IMAGENET_PRODUCTS_DATA_DIR / "imagenet_product_measurement_types.json"
)

CUSTOM_FOOD_CLASSES_PATH = CUSTOM_PRODUCTS_DATA_DIR / "custom_classes.json"
CUSTOM_FOOD_INGREDIENTS_PATH = CUSTOM_PRODUCTS_DATA_DIR / "custom_ingredients.json"
CUSTOM_PRODUCT_MEASUREMENT_TYPES_PATH = (
    CUSTOM_PRODUCTS_DATA_DIR / "custom_product_measurement_types.json"
)

RECIPES_SEED_PATH = RECIPES_DATA_DIR / "recipes_seed.json"

USERS_SEED_PATH = USERS_DATA_DIR / "users_seed.json"
USERS_PRODUCTS_SEED_PATH = USERS_DATA_DIR / "users_products_seed.json"


DATASET_DIR = MACHINE_LEARNING_DIR / "dataset"
RAW_DIR = DATASET_DIR / "raw"
TRAIN_DIR = DATASET_DIR / "train"
VALIDATION_DIR = DATASET_DIR / "validation"
INGREDIENTS_DIR = DATASET_DIR / "ingridients"

LOG_DIR = MACHINE_LEARNING_DIR / "logs"
TRAINED_DIR = MACHINE_LEARNING_DIR / "trained"

MODEL_PATH = TRAINED_DIR / "product_classifier.keras"
