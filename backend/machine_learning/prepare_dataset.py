import random
import shutil

from backend.paths import RAW_DIR, TRAIN_DIR, VALIDATION_DIR

VALIDATION_SPLIT = 0.2
RANDOM_SEED = 42

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def prepare_dataset():

    if not RAW_DIR.exists():
        raise FileNotFoundError(f"Wrong path: {RAW_DIR}")

    classes = [directory for directory in RAW_DIR.iterdir() if directory.is_dir()]

    if not classes:
        raise ValueError("No classes found")

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

        random_generator.shuffle(images)

        validation_count = round(len(images) * (VALIDATION_SPLIT))

        validation_images = images[:validation_count]
        train_images = images[validation_count:]

        for directory in [train_dir, validation_dir]:
            if directory.exists():
                shutil.rmtree(directory)
            directory.mkdir(parents=True, exist_ok=True)

        for image in train_images:
            shutil.copy2(image, train_dir / image.name)

        for image in validation_images:
            shutil.copy2(image, validation_dir / image.name)


if __name__ == "__main__":
    prepare_dataset()
