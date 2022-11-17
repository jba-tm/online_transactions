import pytest

from starlette import status
from typing import TYPE_CHECKING, Callable

from app.conf.config import jwt_settings, settings
from app.contrib.transaction.repository import transaction_repo
from app.contrib.transaction import TransactionStatusChoices, TransactionTypeChoices

if TYPE_CHECKING:
    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_get_transaction_list_api(
        async_client: "AsyncClient",
        get_simple_user: Callable,
        async_db: "AsyncSession",
        get_token_headers: Callable,
        get_wallet: Callable,
) -> None:
    user = await get_simple_user()

    wallet = await get_wallet(user=user, )
    await transaction_repo.create(async_db, obj_in={
        'from_wallet_id': wallet.id,
        'transaction_type': TransactionTypeChoices.REPLENISHMENT.value,
        'total_amount': 200,
        'currency': 'USD',
        'status': TransactionStatusChoices.COMPLETED.value,
    })
    await transaction_repo.create(async_db, obj_in={
        'to_wallet_id': wallet.id,
        'transaction_type': TransactionTypeChoices.WITHDRAW.value,
        'total_amount': 200,
        'currency': 'USD',
        'status': TransactionStatusChoices.COMPLETED.value,
    })

    token_headers = get_token_headers(user, jwt_settings.JWT_AUDIENCE)
    response = await async_client.get(f'{settings.API_V1_STR}/transaction/', headers=token_headers)

    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert len(result.get('rows')) > 0


@pytest.mark.asyncio
async def test_replenish_wallet_api(
        async_client: "AsyncClient",
        get_simple_user: Callable,
        async_db: "AsyncSession",
        get_token_headers: Callable,
        get_wallet: Callable,

) -> None:
    user = await get_simple_user()

    wallet = await get_wallet(user=user)

    token_headers = get_token_headers(user, jwt_settings.JWT_AUDIENCE)
    data = {
        'wallet_id': wallet.id.__str__(),
        'amount': 100
    }
    response = await async_client.post(
        f'{settings.API_V1_STR}/transaction/replenish-wallet/', headers=token_headers,
        json=data
    )
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.asyncio
async def test_withdraw_wallet_api(
        async_client: "AsyncClient",
        get_simple_user: Callable,
        async_db: "AsyncSession",
        get_token_headers: Callable,
        get_wallet: Callable,

) -> None:
    user = await get_simple_user()

    wallet = await get_wallet(user=user)

    token_headers = get_token_headers(user, jwt_settings.JWT_AUDIENCE)
    data = {
        'wallet_id': wallet.id.__str__(),
        'amount': 100
    }
    response = await async_client.post(
        f'{settings.API_V1_STR}/transaction/withdraw-wallet/', headers=token_headers,
        json=data
    )
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.asyncio
async def test_transfer_money_api(
        async_client: "AsyncClient",
        get_simple_user: Callable,
        async_db: "AsyncSession",
        get_token_headers: Callable,
        get_wallet: Callable,
) -> None:
    user = await get_simple_user()
    user_2 = await get_simple_user()
    wallet = await get_wallet(user=user)
    to_wallet = await get_wallet(user=user_2)
    token_headers = get_token_headers(user, jwt_settings.JWT_AUDIENCE)
    data = {
        'from_wallet_id': wallet.id.__str__(),
        'to_wallet_id': to_wallet.id.__str__(),
        'amount': 100
    }
    response = await async_client.post(
        f'{settings.API_V1_STR}/transaction/transfer-money/', headers=token_headers,
        json=data
    )
    assert response.status_code == status.HTTP_201_CREATED

