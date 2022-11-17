from typing import Generator, Optional
from jose import jwt
from fastapi import Depends, HTTPException

from starlette.status import HTTP_403_FORBIDDEN
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.conf.config import settings
from app.contrib.account.repository import user_repo
from app.contrib.account.schema import TokenPayload

from app.core.exceptions import InvalidToken

from app.utils.security import OAuth2PasswordBearerWithCookie, lazy_jwt_settings
from app.core.schema import CommonsModel
from app.db.session import AsyncSessionLocal, SessionLocal

from app.utils.translation import gettext as _
from app.contrib.account.models import User


reusable_oauth2 = OAuth2PasswordBearerWithCookie(
    tokenUrl=f'{settings.ROOT_PATH}{settings.API_V1_STR}/account/token/',
    auto_error=True,
)


async def get_language(lang: Optional[str] = settings.LANGUAGE_CODE):
    return lang


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> Generator:
    try:
        async with AsyncSessionLocal() as session:
            yield session
    finally:
        await session.close()


async def get_current_user(
        async_db: AsyncSession = Depends(get_async_db),
        token: str = Depends(reusable_oauth2),
) -> User:
    """
    Get user by token
    :param async_db:
    :param token:
    :return:
    """

    try:
        payload = lazy_jwt_settings.JWT_DECODE_HANDLER(token)
        token_data = TokenPayload(**payload)
    except (jwt.JWTError, ValidationError) as e:
        raise InvalidToken
    user = await user_repo.first(async_db=async_db, params={'id': token_data.user_id})

    return user


async def get_active_user(user: User = Depends(get_current_user)) -> User:
    if not user.is_active or user.deleted_at is not None:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail=_('Your account is disabled'))
    return user


async def get_commons(
        order_by: Optional[str] = None,
        limit: Optional[int] = settings.PAGINATION_MAX_SIZE,
        page: Optional[int] = 1,
) -> CommonsModel:
    """

    Get commons dict for list pagination and filter
    :param order_by:
    :param limit:
    :param page:
    :return:
    """
    if order_by is None:
        order_by = []
    elif isinstance(order_by, str):
        order_by = order_by.split(',')
    if not page or not isinstance(page, int):
        page = 1
    elif page < 0:
        page = 1
    offset = (page - 1) * limit
    return CommonsModel(
        limit=limit,
        offset=offset,
        page=page,
        order_by=order_by,
    )
