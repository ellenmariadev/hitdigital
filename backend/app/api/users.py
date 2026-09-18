from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.config.settings import Settings, get_settings
from app.models.user import FetchUsersRequest, FetchUsersResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


def get_user_service(request: Request) -> UserService:
    return request.app.state.user_service


ServiceDep = Annotated[UserService, Depends(get_user_service)]
SettingsDep = Annotated[Settings, Depends(get_settings)]


@router.post("/fetch", response_model=FetchUsersResponse)
async def fetch_users(
    payload: FetchUsersRequest,
    service: ServiceDep,
    settings: SettingsDep,
) -> FetchUsersResponse:
    if len(payload.user_ids) > settings.max_user_ids:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"too many user_ids (max {settings.max_user_ids})",
        )
    return await service.fetch_users(payload.user_ids)
