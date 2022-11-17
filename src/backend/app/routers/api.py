from fastapi import APIRouter

from app.contrib.account.api import api as account_api
from app.contrib.transaction.api import api as transaction_api
from app.contrib.wallet.api import api as wallet_api

api = APIRouter()
api.include_router(account_api, tags=['account'], prefix='/account')
api.include_router(transaction_api, tags=['transaction'], prefix='/transaction')
api.include_router(wallet_api, tags=['wallet'], prefix='/wallet')
