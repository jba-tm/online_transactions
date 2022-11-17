import sqlalchemy as sa
from decimal import Decimal
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy_utils import ChoiceType
from sqlalchemy.ext.hybrid import hybrid_property

from app.utils.prices import Money
from app.conf.config import settings
from app.db.models import UUIDMixin, CreationModificationDateMixin, ModelWithMetadataMixin, Base
from app.contrib.transaction import TransactionStatusChoices, TransactionTypeChoices


class Transaction(UUIDMixin, CreationModificationDateMixin, ModelWithMetadataMixin, Base):
    __tablename__: str = 'transaction'

    to_wallet_id = sa.Column(
        UUID(as_uuid=True),
        sa.ForeignKey('wallet.id', ondelete='RESTRICT', name='fx_tr_to_wl_id'),
        nullable=True
    )
    from_wallet_id = sa.Column(
        UUID(as_uuid=True),
        sa.ForeignKey('wallet.id', ondelete='RESTRICT', name='fx_tr_from_wl_id'),
        nullable=True
    )
    currency = sa.Column(
        sa.String(settings.DEFAULT_CURRENCY_CODE_LENGTH),
        default=settings.DEFAULT_CURRENCY_CODE, nullable=False
    )

    total_amount = sa.Column(sa.DECIMAL(precision=12, scale=2), nullable=False)
    transaction_type = sa.Column(
        ChoiceType(choices=TransactionTypeChoices, impl=sa.String(13)), nullable=False,
    )
    status = sa.Column(
        ChoiceType(choices=TransactionStatusChoices, impl=sa.String(10)), nullable=False,
        default=TransactionStatusChoices.PROCESSING
    )

    to_wallet = relationship('Wallet', foreign_keys=[to_wallet_id], lazy='noload')
    from_wallet = relationship('Wallet', foreign_keys=[from_wallet_id], lazy='noload')

    @hybrid_property
    def total(self):
        return Money(amount=Decimal(self.total_amount), currency=self.currency)
