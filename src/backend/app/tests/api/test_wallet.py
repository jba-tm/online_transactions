from pprint import pprint

import pytest

from starlette import status
from typing import TYPE_CHECKING, Callable

from app.contrib.wallet.repository import wallet_repo
from app.conf.config import jwt_settings, settings

if TYPE_CHECKING:
    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_get_wallet_list_api(

        async_client: "AsyncClient",
        get_simple_user: Callable,
        async_db: "AsyncSession",
        get_token_headers: Callable,
        get_wallet: Callable,
) -> None:
    user = await get_simple_user()
    wallet = await get_wallet(user)

    token_headers = get_token_headers(user, jwt_settings.JWT_AUDIENCE)
    response = await async_client.get(f'{settings.API_V1_STR}/wallet/', headers=token_headers)

    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert len(result.get('rows')) > 0


@pytest.mark.asyncio
async def test_get_wallet_detail_api(
        async_client: "AsyncClient",
        get_simple_user: Callable,
        async_db: "AsyncSession",
        get_token_headers: Callable,
        get_wallet: Callable,
) -> None:
    user = await get_simple_user()
    wallet = await get_wallet(user)
    token_headers = get_token_headers(user, jwt_settings.JWT_AUDIENCE)
    response = await async_client.get(f'{settings.API_V1_STR}/wallet/{wallet.id}/detail/', headers=token_headers)

    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert result.get('id') == wallet.id.__str__()


@pytest.mark.asyncio
async def test_create_wallet_api(
        async_client: "AsyncClient",
        get_simple_user: Callable,
        async_db: "AsyncSession",
        get_token_headers: Callable,
) -> None:
    user = await get_simple_user()

    token_headers = get_token_headers(user, jwt_settings.JWT_AUDIENCE)
    data = {
        'currency': settings.DEFAULT_CURRENCY_CODE,
    }
    response = await async_client.post(f'{settings.API_V1_STR}/wallet/create/', headers=token_headers, json=data)

    # assert response.status_code == status.HTTP_201_CREATED

    result = response.json()
    pprint(result)
