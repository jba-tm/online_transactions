import sqlalchemy as sa

from app.db.models import UUIDMixin, Base, CreationModificationDateMixin, ModelWithMetadataMixin


class User(UUIDMixin, CreationModificationDateMixin, ModelWithMetadataMixin, Base):
    __tablename__: str = 'user'
    full_name = sa.Column(sa.String(255), nullable=False)
    hashed_password = sa.Column(sa.String(500))
    email = sa.Column(sa.String(255), unique=True, index=True, nullable=True)
    is_superuser = sa.Column(sa.Boolean, default=False, nullable=False)

    is_active = sa.Column(sa.Boolean, default=True, nullable=False)
    email_confirmed_at = sa.Column(sa.DateTime(timezone=True), )
    deleted_at = sa.Column(sa.DateTime(timezone=True))
    language_code = sa.Column(sa.String(5), nullable=True)
