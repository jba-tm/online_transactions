from decimal import Decimal
from typing import TYPE_CHECKING, Union, List

from app.utils.prices import Money

from .schema import TransactionInfo

if TYPE_CHECKING:
    from .models import Transaction
    from sqlalchemy.engine.row import Row


def fetch_transaction_info(transaction: Union["Transaction", "Row"]) -> TransactionInfo:
    return TransactionInfo(
        id=transaction.id,
        status=transaction.status,
        transaction_type=transaction.transaction_type,
        total=Money(amount=Decimal(transaction.total_amount), currency=transaction.currency),
        to_wallet_id=transaction.to_wallet_id,
        from_wallet_id=transaction.from_wallet_id,
    )


def fetch_transaction_info_list(transactions: List[Union["Transaction", "Row"]]) -> List[TransactionInfo]:
    return list(fetch_transaction_info(transaction) for transaction in transactions)
