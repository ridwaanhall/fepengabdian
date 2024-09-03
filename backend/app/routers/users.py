from fastapi import APIRouter

from app.dependencies import user_dependency

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=user_dependency)
async def read_users_me(current_user: user_dependency):
    return current_user
