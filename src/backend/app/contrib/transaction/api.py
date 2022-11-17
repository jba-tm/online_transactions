from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from pydantic.error_wrappers import ErrorWrapper
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import load_only

from app.routers.dependency import get_async_db, get_current_user, get_commons, get_active_user
from app.core.schema import CommonsModel, IPaginationDataBase, IResponseBase
from app.contrib.account.models import User
from app.utils.translation import gettext as _
from app.contrib.wallet.repository import wallet_repo
from app.contrib.transaction import TransactionTypeChoices

from .fetch import fetch_transaction_info_list
from .repository import transaction_repo
from .schema import TransactionVisible, TransactionReplenishWallet, TransactionWithdrawWallet, TransactionTransferMoney
from .tasks import transaction_replenish_wallet_task, transaction_withdraw_wallet_task, transaction_transfer_money_task

api = APIRouter()


@api.get('/', name='transaction-list', response_model=IPaginationDataBase[TransactionVisible])
async def get_transaction_list(
        async_db: AsyncSession = Depends(get_async_db),
        user: User = Depends(get_current_user),
        commons: CommonsModel = Depends(get_commons)
) -> dict:
    # query = text('select tr."id" as id  from public."transaction" as tr')
    sql_text = '''
        select tr."id" as id,
            tr."from_wallet_id", 
            tr."to_wallet_id",
            tr."currency",
            tr."total_amount",
            tr."status",
            tr."transaction_type"
        from public."transaction" tr 
        where   tr."to_wallet_id" in (select w."id" from public."wallet" w where w."user_id"=:user_id)
         or     tr."from_wallet_id" in (select w."id" from public."wallet" w where w."user_id"=:user_id)
    '''
    result = await transaction_repo.execute_raw_sql(async_db, sql_text=sql_text, params={'user_id': user.id})
    transaction_info_list = fetch_transaction_info_list(transactions=result)
    sql_text_count = '''
            select count(tr."id")
            from public."transaction" tr 
            where   tr."to_wallet_id" in (select w."id" from public."wallet" w where w."user_id"=:user_id)
             or     tr."from_wallet_id" in (select w."id" from public."wallet" w where w."user_id"=:user_id)
        '''
    result = await transaction_repo.execute_raw_sql(async_db, sql_text=sql_text_count, params={'user_id': user.id})
    count = result.fetchone()
    return {
        'rows': transaction_info_list,
        'count': count.count,
        'limit': commons.limit,
        'page': commons.page
    }


@api.post('/replenish-wallet/', name='transaction-replenish-wallet',
          response_model=IResponseBase[TransactionVisible],
          status_code=status.HTTP_201_CREATED)
async def transaction_replenish_wallet(
        obj_in: TransactionReplenishWallet,
        user: User = Depends(get_active_user),
        async_db: AsyncSession = Depends(get_async_db)
) -> dict:
    is_exist = await wallet_repo.exists(async_db, params={'user_id': user.id, 'id': obj_in.wallet_id})

    if not is_exist:
        raise RequestValidationError(
            [ErrorWrapper(ValueError(_('Wallet does not exist')), ("body", 'wallet_id',))])
    db_obj = await transaction_repo.create(async_db, obj_in={
        'to_wallet_id': obj_in.wallet_id,
        'total_amount': obj_in.amount,
        'transaction_type': TransactionTypeChoices.REPLENISHMENT.value
    })
    transaction_replenish_wallet_task.delay(transaction_id=db_obj.id.__str__())
    return {
        'message': _('Transaction successfully created'),
        'data': db_obj
    }


@api.post(
    '/withdraw-wallet/', name='transaction-withdraw-wallet',
    response_model=IResponseBase[TransactionVisible],
    status_code=status.HTTP_201_CREATED)
async def transaction_withdraw_wallet(
        obj_in: TransactionWithdrawWallet,

        user: User = Depends(get_active_user),
        async_db: AsyncSession = Depends(get_async_db)
) -> dict:
    wallet = await wallet_repo.first(
        async_db, params={'user_id': user.id, 'id': obj_in.wallet_id},
        options=(load_only('id', 'total_amount'),)
    )
    if not wallet:
        raise RequestValidationError(
            [ErrorWrapper(ValueError(_('Wallet does not exist')), ("body", 'wallet_id',))])
    if wallet.total_amount < obj_in.amount:
        raise RequestValidationError(
            [ErrorWrapper(ValueError(_('Not enough amount')), ("body", 'amount',))])
    db_obj = await transaction_repo.create(async_db, obj_in={
        'from_wallet_id': obj_in.wallet_id,
        'total_amount': obj_in.amount,
        'transaction_type': TransactionTypeChoices.WITHDRAW.value
    })
    transaction_withdraw_wallet_task.delay(transaction_id=db_obj.id.__str__())

    return {
        'message': _('Transaction successfully created'),
        'data': db_obj
    }


@api.post(
    '/transfer-money/', name='transaction-transfer-money',
    response_model=IResponseBase[TransactionVisible],
    status_code=status.HTTP_201_CREATED
)
async def transaction_transfer_money(
        obj_in: TransactionTransferMoney,
        user: User = Depends(get_active_user),
        async_db: AsyncSession = Depends(get_async_db)
) -> dict:
    from_wallet = await wallet_repo.first(
        async_db, params={'user_id': user.id, 'id': obj_in.from_wallet_id},
        options=(load_only('id', 'total_amount', 'currency'),)
    )
    if not from_wallet:
        raise RequestValidationError(
            [ErrorWrapper(ValueError(_('Wallet does not exist')), ("body", 'wallet_id',))])
    if from_wallet.total_amount < obj_in.amount:
        raise RequestValidationError(
            [ErrorWrapper(ValueError(_('Not enough amount')), ("body", 'amount',))])
    to_wallet = await wallet_repo.first(async_db, params={'id': obj_in.to_wallet_id},
                                        options=(load_only('id', 'currency'),))
    if not to_wallet:
        raise RequestValidationError(
            [ErrorWrapper(ValueError(_('Wallet does not exist')), ("body", 'to_wallet_id',))])
    if from_wallet.currency != to_wallet.currency:
        raise RequestValidationError(
            [ErrorWrapper(ValueError(_('Invalid currency')), ("body", 'from_wallet_id',))])
    db_obj = await transaction_repo.create(async_db, obj_in={
        'from_wallet_id': obj_in.from_wallet_id,
        'to_wallet_id': obj_in.to_wallet_id,
        'total_amount': obj_in.amount,
        'transaction_type': TransactionTypeChoices.TRANSFER.value
    })
    transaction_transfer_money_task.delay(transaction_id=db_obj.id.__str__())

    return {
        'message': _('Transaction successfully created'),
        'data': db_obj
    }


@api.get('/{obj_id}/detail/', name='transaction-detail', response_model=TransactionVisible)
async def get_single_transaction(
        obj_id: UUID,
        user: User = Depends(get_current_user),
        async_db: AsyncSession = Depends(get_async_db)

) -> dict:
    sql_text = '''
        select tr."id" as id,
            tr."from_wallet_id", 
            tr."to_wallet_id",
            tr."currency",
            tr."total_amount",
            tr."status",
            tr."transaction_type"
        from public."transaction" tr 
        where   (tr."to_wallet_id" in (select w."id" from public."wallet" w where w."user_id"=:user_id)
         or     tr."from_wallet_id" in (select w."id" from public."wallet" w where w."user_id"=:user_id))
         and tr."id"=:transaction_id
    '''
    result = await transaction_repo.execute_raw_sql(async_db, sql_text=sql_text,
                                                    params={'user_id': user.id, 'transaction_id': obj_id})
    db_obj = result.fetchone()
    if db_obj is None:
        transaction_repo.does_not_exist()
    return {
        'id': db_obj.id,
        'total': {
            'amount': db_obj.total_amount,
            'currency': db_obj.currency,
        },
        'from_wallet_id': db_obj.from_wallet_id,
        'to_wallet_id': db_obj.to_wallet_id,
        'status': db_obj.status,
        'transaction_type': db_obj.transaction_type,
    }
