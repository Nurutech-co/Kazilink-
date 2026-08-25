from fastapi import APIRouter
from app.api.v1.routes import mpesa

api_router = APIRouter()

api_router.include_router(
    mpesa.router,
    prefix="/payments/mpesa",
    tags=["mpesa"],
)
