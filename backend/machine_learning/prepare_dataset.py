import json
import math
import random
import shutil

from machine_learning.errors.prepare_dataset_error import (
    EmptyDatasetClassesError,
    IngredientsFileNotFoundError,
    InvalidIngredientsFileError,
    RawDatasetNotFoundError,
)
from paths import INGREDIENTS_DIR, RAW_DIR, TRAIN_DIR, VALIDATION_DIR

VALIDATION_SPLIT = 0.2
RANDOM_SEED = 42

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".jfif", ".png", ".webp"}

REQUIRED_INGREDIENTS_FIELDS = {
    "calories",
    "protein",
    "carbs",
    "fat",
    "average_size",
    "shelf_life",
}

REQUIRED_INGREDIENTS_FIELDS = {
    "calories",
    "protein",
    "carbs",
    "fat",
    "average_size",
    "shelf_life",
}


def prepare_dataset():

    _create_dirs()
    classes, ingredients = _validate_data()

    for class_name, data in ingredients.items():
        ingredients_path = INGREDIENTS_DIR / f"{class_name}.json"

        with open(ingredients_path, "w", encoding="utf-8") as file:
            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=4,
            )

    random_generator = random.Random(RANDOM_SEED)

    for class_dir in classes:
        class_name = class_dir.name

        train_dir = TRAIN_DIR / class_name
        validation_dir = VALIDATION_DIR / class_name

        images = [
            file
            for file in class_dir.iterdir()
            if file.is_file() and file.suffix.lower() in IMAGE_EXTENSIONS
        ]
        training_filenames = [_training_filename(image) for image in images]
        if len(training_filenames) != len(set(training_filenames)):
            raise ValueError(f"Multiple images map to the same filename in {class_dir}")

        random_generator.shuffle(images)

        validation_count = round(len(images) * (VALIDATION_SPLIT))

        validation_images = images[:validation_count]
        train_images = images[validation_count:]

        for directory in [train_dir, validation_dir]:
            if directory.exists():
                shutil.rmtree(directory)
            directory.mkdir(parents=True, exist_ok=True)

        for image in train_images:
            shutil.copy2(image, train_dir / _training_filename(image))

        for image in validation_images:
            shutil.copy2(image, validation_dir / _training_filename(image))


def _training_filename(image):
    if image.suffix.lower() == ".jfif":
        return image.with_suffix(".jpg").name
    return image.name


def _validate_data():
    if not RAW_DIR.exists():
        raise RawDatasetNotFoundError(f"Wrong path: {RAW_DIR}")

    classes = sorted(directory for directory in RAW_DIR.iterdir() if directory.is_dir())

    if not classes:
        raise EmptyDatasetClassesError("No classes found")

    validated_ingredients = {}

    for class_dir in classes:
        class_name = class_dir.name
        ingredients_path = class_dir / "ingredients.json"

        if not ingredients_path.is_file():
            raise IngredientsFileNotFoundError(
                f"Missing ingredients.json for class: {class_name}"
            )

        try:
            with open(ingredients_path, "r", encoding="utf-8") as file:
                ingredients = json.load(file)

        except (json.JSONDecodeError, OSError) as error:
            raise InvalidIngredientsFileError(
                f"Cannot read ingredients.json for {class_name}: {error}"
            ) from error

        if not isinstance(ingredients, dict):
            raise InvalidIngredientsFileError(
                f"Invalid JSON structure for class: {class_name}"
            )

        missing_fields = REQUIRED_INGREDIENTS_FIELDS - ingredients.keys()

        if missing_fields:
            raise InvalidIngredientsFileError(
                f"Missing fields in {class_name}: {missing_fields}"
            )

        for field in REQUIRED_INGREDIENTS_FIELDS:
            value = ingredients[field]

            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
                or value < 0
            ):
                raise InvalidIngredientsFileError(
                    f"Invalid value for '{field}' in class: {class_name}"
                )

        validated_ingredients[class_name] = ingredients

    return classes, validated_ingredients


def _create_dirs():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    VALIDATION_DIR.mkdir(parents=True, exist_ok=True)
    INGREDIENTS_DIR.mkdir(parents=True, exist_ok=True)


def _validate_data():
    if not RAW_DIR.exists():
        raise RawDatasetNotFoundError(f"Wrong path: {RAW_DIR}")

    classes = sorted(directory for directory in RAW_DIR.iterdir() if directory.is_dir())

    if not classes:
        raise EmptyDatasetClassesError("No classes found")

    validated_ingredients = {}

    for class_dir in classes:
        class_name = class_dir.name
        ingredients_path = class_dir / "ingredients.json"

        if not ingredients_path.is_file():
            raise IngredientsFileNotFoundError(
                f"Missing ingredients.json for class: {class_name}"
            )

        try:
            with open(ingredients_path, "r", encoding="utf-8") as file:
                ingredients = json.load(file)

        except (json.JSONDecodeError, OSError) as error:
            raise InvalidIngredientsFileError(
                f"Cannot read ingredients.json for {class_name}: {error}"
            ) from error

        if not isinstance(ingredients, dict):
            raise InvalidIngredientsFileError(
                f"Invalid JSON structure for class: {class_name}"
            )

        missing_fields = REQUIRED_INGREDIENTS_FIELDS - ingredients.keys()

        if missing_fields:
            raise InvalidIngredientsFileError(
                f"Missing fields in {class_name}: {missing_fields}"
            )

        for field in REQUIRED_INGREDIENTS_FIELDS:
            value = ingredients[field]

            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
                or value < 0
            ):
                raise InvalidIngredientsFileError(
                    f"Invalid value for '{field}' in class: {class_name}"
                )

        validated_ingredients[class_name] = ingredients

    return classes, validated_ingredients


def _create_dirs():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    VALIDATION_DIR.mkdir(parents=True, exist_ok=True)
    INGREDIENTS_DIR.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    prepare_dataset()
