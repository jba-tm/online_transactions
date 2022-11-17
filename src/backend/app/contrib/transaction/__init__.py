from app.utils.translation import gettext_lazy as _

from app.core.enums import TextChoices


class TransactionTypeChoices(TextChoices):
    TRANSFER = 'transfer'
    REPLENISHMENT = 'replenishment'
    WITHDRAW = 'withdraw'


TransactionTypeChoices.TRANSFER.label = _('transfer')
TransactionTypeChoices.REPLENISHMENT.label = _('replenishment')
TransactionTypeChoices.WITHDRAW.label = _('withdraw')


class TransactionStatusChoices(TextChoices):
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    REJECTED = 'rejected'


TransactionStatusChoices.PROCESSING.label = _('processing')
TransactionStatusChoices.COMPLETED.label = _('completed')
TransactionStatusChoices.REJECTED.label = _('rejected')
