from app.db.repository import CRUDBase, CRUDBaseSync

from .models import Transaction


class CRUDTransactionSync(CRUDBaseSync[Transaction]):
    pass


class CRUDTransaction(CRUDBase[Transaction]):
    pass


transaction_repo = CRUDTransaction(Transaction)
transaction_repo_sync = CRUDTransactionSync(Transaction)
