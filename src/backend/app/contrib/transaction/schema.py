from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional
from dataclasses import dataclass

from app.contrib.transaction import TransactionStatusChoices, TransactionTypeChoices
from app.core.schema import MoneyBase
from app.utils.prices import Money


class TransactionVisible(BaseModel):
    id: UUID
    status: TransactionStatusChoices
    total: MoneyBase
    transaction_type: TransactionTypeChoices = Field(..., alias='transactionType')
    to_wallet_id: Optional[UUID] = Field(None, alias='toWalletId')
    from_wallet_id: Optional[UUID] = Field(None, alias='fromWalletId')
    created_at: Optional[datetime] = Field(None, alias='createdAt')

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class TransactionReplenishWallet(BaseModel):
    wallet_id: UUID = Field(..., alias='walletId')
    amount: Decimal

    class Config:
        allow_population_by_field_name = True


class TransactionWithdrawWallet(BaseModel):
    wallet_id: UUID = Field(..., alias='walletId')
    amount: Decimal

    class Config:
        allow_population_by_field_name = True


class TransactionTransferMoney(BaseModel):
    from_wallet_id: UUID = Field(..., alias='fromWalletId')
    to_wallet_id: UUID = Field(..., alias='toWalletId')
    amount: Decimal

    class Config:
        allow_population_by_field_name = True


@dataclass
class TransactionInfo:
    id: UUID
    status: TransactionStatusChoices
    total: Money
    transaction_type: TransactionTypeChoices
    to_wallet_id: Optional[UUID] = None
    from_wallet_id: Optional[UUID] = None
