from uuid import UUID
from sqlalchemy import text

from app.core.celery_app import celery_app, DatabaseTask
from app.contrib.wallet.repository import wallet_repo_sync
from app.contrib.transaction import TransactionStatusChoices
from .repository import transaction_repo_sync


@celery_app.task(
    base=DatabaseTask,
    acks_late=True, bind=True, retry=True,
    retry_policy=dict(
        max_retries=3,
        interval_start=3,
        interval_step=1,
        interval_max=6
    ))
def transaction_replenish_wallet_task(self: DatabaseTask, transaction_id: UUID):
    session = next(self.get_session())
    transaction = transaction_repo_sync.first(session, params={'id': transaction_id}, )
    if not transaction:
        raise Exception('Transaction doest not exist - %(transaction_id)s' % {'transaction_id': transaction_id})
    wallet = wallet_repo_sync.get(session, obj_id=transaction.to_wallet_id)
    amount = wallet.total_amount + transaction.total_amount

    wallet.total_amount = amount
    transaction.status = TransactionStatusChoices.COMPLETED
    session.add(wallet)
    session.add(transaction)
    session.commit()
    return 'Transaction successfully completed'


@celery_app.task(
    base=DatabaseTask,
    acks_late=True, bind=True, retry=True,
    retry_policy=dict(
        max_retries=3,
        interval_start=3,
        interval_step=1,
        interval_max=6
    ))
def transaction_withdraw_wallet_task(self: DatabaseTask, transaction_id: UUID):
    session = next(self.get_session())

    transaction = transaction_repo_sync.first(session, params={'id': transaction_id}, )
    if not transaction:
        raise Exception('Transaction doest not exist - %(transaction_id)s' % {'transaction_id': transaction_id})
    wallet = wallet_repo_sync.get(session, obj_id=transaction.from_wallet_id)
    if wallet.total_amount < transaction.total_amount:
        transaction.status = TransactionStatusChoices.REJECTED
        session.add(transaction)
        session.commit()
        return 'Transaction rejected'
    wallet.total_amount = wallet.total_amount - transaction.total_amount
    transaction.status = TransactionStatusChoices.COMPLETED
    session.add(wallet)
    session.add(transaction)
    session.commit()
    return 'Transaction successfully completed'


@celery_app.task(
    base=DatabaseTask,
    acks_late=True, bind=True, retry=True,
    retry_policy=dict(
        max_retries=3,
        interval_start=3,
        interval_step=1,
        interval_max=6
    ))
def transaction_transfer_money_task(self: DatabaseTask, transaction_id: UUID):
    session = next(self.get_session())
    transaction = transaction_repo_sync.first(session, params={'id': transaction_id}, )
    if not transaction:
        raise Exception('Transaction doest not exist - %(transaction_id)s' % {'transaction_id': transaction_id})
    from_wallet = wallet_repo_sync.get(session, obj_id=transaction.from_wallet_id)
    if from_wallet.total_amount < transaction.total_amount:
        transaction.status = TransactionStatusChoices.REJECTED
        session.add(transaction)
        session.commit()
        return 'Transaction rejected'
    to_wallet = wallet_repo_sync.get(session, obj_id=transaction.to_wallet_id)
    if from_wallet.currency != to_wallet.currency:
        transaction.status = TransactionStatusChoices.REJECTED
        session.add(transaction)
        session.commit()
        return 'Transaction rejected'

    from_wallet.total_amount = from_wallet.total_amount - transaction.total_amount
    to_wallet.total_amount = from_wallet.total_amount + transaction.total_amount
    transaction.status = TransactionStatusChoices.COMPLETED
    session.add(from_wallet)
    session.add(to_wallet)
    session.add(transaction)
    session.commit()
    return 'Transaction successfully completed'
