from fastapi import APIRouter

from app.api.v1.endpoints import products_router, auth_router

api_router = APIRouter()
api_router.include_router(products_router, tags=["Wildberries products"])

api_router.include_router(auth_router, tags=["API auth"])
