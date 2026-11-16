class TrainingError(Exception):
    """Base exception for machine learning training errors."""


class RawDatasetNotFoundError(FileNotFoundError, TrainingError):
    """Dataset/raw not found"""


class EmptyDatasetClassesError(FileNotFoundError, TrainingError):
    """Dataset/raw is empty. No classes founded"""


class IngredientsFileNotFoundError(FileNotFoundError, TrainingError):
    """File of new class'es ingridients trained not found"""


class InvalidIngredientsFileError(ValueError, TrainingError):
    """Fields of file are missing or incorrect"""
