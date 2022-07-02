from fastapi import APIRouter
from app.controllers import affiliate

router = APIRouter()

router.include_router(affiliate.router)
