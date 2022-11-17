from fastapi import Depends, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from pydantic.error_wrappers import ErrorWrapper
from fastapi.exceptions import RequestValidationError
from starlette.status import HTTP_201_CREATED
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.translation import gettext as _
from app.routers.dependency import get_current_user, get_async_db
from app.utils.security import lazy_jwt_settings
from app.core.schema import IResponseBase
from app.contrib.account.schema import SignUp
from app.utils.datetime.timezone import now

from .models import User
from .repository import user_repo
from .schema import UserVisible, Token

api = APIRouter()


@api.get('/me/', response_model=UserVisible)
async def me(
        user: User = Depends(get_current_user),
) -> User:
    """
    Retrieve logged user
    :param user:
    :return:
    """

    return user


@api.post('/token/', response_model=Token)
async def get_token(
        data: OAuth2PasswordRequestForm = Depends(),
        async_db: AsyncSession = Depends(get_async_db),
) -> dict:
    """
    Get token from external api
    """
    user = await user_repo.authenticate(
        async_db,
        email=data.username,
        password=data.password,
    )

    if not user:
        raise RequestValidationError(
            [ErrorWrapper(ValueError(_('Incorrect email or password')), ("body", 'email'))])
    if not user.is_active:
        raise RequestValidationError(
            [ErrorWrapper(ValueError(_('Inactive user')), ("body", 'non_field_errors'))]
        )

    payload = lazy_jwt_settings.JWT_PAYLOAD_HANDLER(
        {
            'user_id': str(user.id),
            'aud': lazy_jwt_settings.JWT_AUDIENCE,
        },
    )
    jwt_token = lazy_jwt_settings.JWT_ENCODE_HANDLER(payload)
    result = {'access_token': jwt_token, 'token_type': 'bearer'}
    if lazy_jwt_settings.JWT_ALLOW_REFRESH:
        refresh_payload = lazy_jwt_settings.JWT_PAYLOAD_HANDLER(
            {'user_id': str(user.id), },
            expires_delta=lazy_jwt_settings.JWT_REFRESH_EXPIRATION_DELTA)
        refresh = lazy_jwt_settings.JWT_ENCODE_HANDLER(refresh_payload)
        result['refresh_token'] = refresh
    return result


@api.post(
    '/sign-up/',
    name='sign-up',
    response_model=IResponseBase[UserVisible],
    status_code=HTTP_201_CREATED,
)
async def sign_up(
        obj_in: SignUp,
        async_db: AsyncSession = Depends(get_async_db),
) -> dict:
    email_exist = await user_repo.exists(async_db, params={'email': obj_in.email})
    if email_exist:
        raise RequestValidationError(
            [ErrorWrapper(ValueError(_('Email with this user already exist')), ("body", 'email'))])
    db_obj = await user_repo.create(
        async_db,
        obj_in={
            'email': obj_in.email,
            'password': obj_in.password,
            'full_name': obj_in.full_name,
            'is_active': True,
            'email_confirmed_at': now()
        }
    )
    return {
        'data': db_obj,
        'message': _('User successfully created')
    }
