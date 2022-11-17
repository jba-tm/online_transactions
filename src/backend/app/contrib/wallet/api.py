from uuid import UUID

from starlette import status
from fastapi import Depends, APIRouter
from pydantic.error_wrappers import ErrorWrapper
from fastapi.exceptions import RequestValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.contrib.account.models import User
from app.contrib.wallet.models import Wallet
from app.contrib.wallet.repository import wallet_repo
from app.contrib.wallet.schema import WalletVisible
from app.routers.dependency import get_current_user, get_async_db, get_commons
from app.core.schema import CommonsModel, IPaginationDataBase
from app.utils.translation import gettext as _

from .schema import WalletCreate

api = APIRouter()


@api.get('/', name='wallet-list', response_model=IPaginationDataBase[WalletVisible])
async def get_wallet_list(
        async_db: AsyncSession = Depends(get_async_db),
        user: User = Depends(get_current_user),
        commons: CommonsModel = Depends(get_commons),
) -> dict:
    object_list = await wallet_repo.get_all(
        async_db, q={'user_id': user.id}, limit=commons.limit,
        offset=commons.offset
    )
    count = await wallet_repo.count(async_db, params={'user_id': user.id})
    return {
        'count': count,
        'rows': object_list,
        'page': commons.page,
        'limit': commons.limit,
    }


@api.post('/create/', name='wallet-create', response_model=WalletVisible, status_code=status.HTTP_201_CREATED)
async def create_wallet(
        obj_in: WalletCreate,
        user: User = Depends(get_current_user),
        async_db: AsyncSession = Depends(get_async_db),
) -> Wallet:
    params = {'user_id': user.id, 'currency': obj_in.currency}
    is_exist = await wallet_repo.exists(async_db=async_db, params=params)

    if is_exist:
        raise RequestValidationError(
            [ErrorWrapper(ValueError(_('Currency wallet already exist')), ("body", 'currency',))])

    wallet = await wallet_repo.create(async_db, obj_in=params)
    return wallet


@api.get('/{obj_id}/detail/', name='wallet-detail', response_model=WalletVisible)
async def get_single_wallet(
        obj_id: UUID,
        async_db: AsyncSession = Depends(get_async_db),
        user: User = Depends(get_current_user),
) -> Wallet:
    return await wallet_repo.get_by_params(async_db, params={'id': obj_id, 'user_id': user.id})
