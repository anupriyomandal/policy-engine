from fastapi import APIRouter

from app.api.routes.policy import router as policy_router

api_router = APIRouter()
api_router.include_router(policy_router)
