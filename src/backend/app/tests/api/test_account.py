import pytest

from faker import Faker
from starlette import status
from typing import TYPE_CHECKING, Callable

from app.conf.config import settings

from app.contrib.account.repository import user_repo

if TYPE_CHECKING:
    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_get_token_api(
        async_client: "AsyncClient",
        get_simple_user: Callable,
) -> None:
    user = await get_simple_user()
    data = {
        'username': user.email,
        'password': 'secret'
    }
    response = await async_client.post(f'{settings.API_V1_STR}/account/token/', data=data)

    result = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert 'access_token' in result


@pytest.mark.asyncio
async def test_sign_up_api(
        async_db: "AsyncSession",
        async_client: "AsyncClient",
        faker: "Faker"
) -> None:
    """
    Test sign up user
    :param async_client:
    :return:
    """
    data = {
        'full_name': faker.name(),
        'email': faker.unique.email(),
        'password': 'secret',
        'password_confirm': 'secret',
    }
    response = await async_client.post(f'{settings.API_V1_STR}/account/sign-up/', json=data)

    assert response.status_code == status.HTTP_201_CREATED

    user_exist = await user_repo.exists(async_db, params={'email': data.get('email')})
    assert user_exist is True
