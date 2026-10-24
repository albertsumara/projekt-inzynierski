from fastapi import APIRouter, File, HTTPException, UploadFile, status
from models.image_classifier import ImageClassifier

from app.schemas.recognition import RecognitionResponse
from app.services.image_service import ImageService, InvalidImageError
from app.services.product_service import ProductService

router = APIRouter()

image_service = ImageService()
image_classifier = ImageClassifier()

product_service = ProductService(
    image_service=image_service,
    image_classifier=image_classifier,
)


@router.post(
    "/product/recognize",
    response_model=RecognitionResponse,
    status_code=status.HTTP_200_OK,
)
async def recognize(
    file: UploadFile = File(...),
) -> RecognitionResponse:
    image_bytes = await file.read()

    try:
        recognitions = product_service.recognize_product(
            image_bytes=image_bytes,
            content_type=file.content_type,
        )
    except InvalidImageError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    finally:
        await file.close()

    return RecognitionResponse(
        filename=file.filename or "uploaded-image",
        recognitions=recognitions,
    )
