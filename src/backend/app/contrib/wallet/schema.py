from datetime import datetime

from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

from app.conf.config import settings
from app.core.schema import MoneyBase


class WalletBase(BaseModel):
    currency: Optional[str] = Field(None, max_length=settings.DEFAULT_CURRENCY_CODE_LENGTH)


class WalletCreate(WalletBase):
    currency: str = Field(..., max_length=settings.DEFAULT_CURRENCY_CODE_LENGTH)


class WalletVisible(BaseModel):
    id: UUID
    total: MoneyBase
    is_active: bool = Field(..., alias='isActive')
    created_at: Optional[datetime] = Field(None, alias='createdAt')

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
