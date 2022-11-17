from app.db.repository import CRUDBase, CRUDBaseSync

from .models import Wallet


class CRUDWalletSync(CRUDBaseSync[Wallet]):
    pass


class CRUDWallet(CRUDBase[Wallet]):
    pass


wallet_repo = CRUDWallet(Wallet)
wallet_repo_sync = CRUDWalletSync(Wallet)
