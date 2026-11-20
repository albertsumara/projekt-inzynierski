from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.user import AddProductToUserRequest
from app.services.user_service import UserService

user_router = APIRouter()


@user_router.post("/user/product", status_code=201)
def add_product_to_user(
    request: AddProductToUserRequest,
    db: Annotated[Session, Depends(get_db)],
):
    return UserService.add_product_to_user(request, db)
