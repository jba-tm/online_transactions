import sqlalchemy as sa
from decimal import Decimal
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

from app.utils.prices import Money
from app.conf.config import settings
from app.db.models import UUIDMixin, CreationModificationDateMixin, ModelWithMetadataMixin, Base


class Wallet(UUIDMixin, CreationModificationDateMixin, ModelWithMetadataMixin, Base):
    __tablename__: str = 'wallet'
    user_id = sa.Column(
        UUID(as_uuid=True), sa.ForeignKey('user.id', ondelete='RESTRICT', name='fx_wl_user_id'),
        nullable=False
    )
    currency = sa.Column(
        sa.String(settings.DEFAULT_CURRENCY_CODE_LENGTH),
        default=settings.DEFAULT_CURRENCY_CODE, nullable=False
    )

    total_amount = sa.Column(sa.DECIMAL(precision=12, scale=2), nullable=False, default=0.0)
    is_active = sa.Column(sa.Boolean, default=True)

    user = relationship('User', lazy='noload')
    __table_args__ = (
        sa.UniqueConstraint('user_id', 'currency', name='ux_user_id_currency'),
    )

    @hybrid_property
    def total(self) -> Money:
        return Money(amount=Decimal(self.total_amount), currency=self.currency)
