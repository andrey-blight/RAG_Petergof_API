from fastapi import APIRouter

from API.app import rag_router, auth_router, statistic_router

api_router = APIRouter()
api_router.include_router(rag_router, tags=["Rag endpoints"])

api_router.include_router(auth_router, tags=["API auth"])

api_router.include_router(statistic_router, tags=["Statistic endpoints"])
