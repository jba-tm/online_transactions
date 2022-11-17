from typing import Any

import sqlalchemy as sa
import re

from uuid import uuid4
from sqlalchemy.orm import declarative_mixin
from sqlalchemy.ext.declarative import declared_attr, declarative_base

from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.hybrid import hybrid_method

PlainBase = declarative_base()


class Base(PlainBase):
    __name__: str
    __abstract__ = True

    id = sa.Column(sa.Integer, primary_key=True, index=True)

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        pattern = re.compile(r'(?<!^)(?=[A-Z])')
        return pattern.sub('_', cls.__name__).lower()


@declarative_mixin
class UUIDMixin:
    id = sa.Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4, nullable=False)


@declarative_mixin
class CreationModificationDateMixin:
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=func.now())
    updated_at = sa.Column(sa.DateTime(timezone=True), onupdate=func.now(), )


@declarative_mixin
class ModelWithMetadataMixin:
    private_metadata = sa.Column(sa.JSON, default={}, nullable=False)
    public_metadata = sa.Column(sa.JSON, default={}, nullable=False)

    @hybrid_method
    def get_value_from_private_metadata(self, key: str, default: Any = None) -> Any:
        return self.private_metadata.get(key, default)

    @hybrid_method
    def store_value_in_private_metadata(self, items: dict):
        if not self.private_metadata:
            self.private_metadata = {}
        self.private_metadata.update(items)

    @hybrid_method
    def clear_private_metadata(self):
        self.private_metadata = {}

    @hybrid_method
    def delete_value_from_private_metadata(self, key: str):
        if key in self.private_metadata:
            del self.private_metadata[key]

    @hybrid_method
    def get_value_from_metadata(self, key: str, default: Any = None) -> Any:
        return self.public_metadata.get(key, default)

    @hybrid_method
    def store_value_in_metadata(self, items: dict):
        if not self.public_metadata:
            self.public_metadata = {}
        self.public_metadata.update(items)

    @hybrid_method
    def clear_metadata(self):
        self.public_metadata = {}

    @hybrid_method
    def delete_value_from_metadata(self, key: str):
        if key in self.public_metadata:
            del self.public_metadata[key]
