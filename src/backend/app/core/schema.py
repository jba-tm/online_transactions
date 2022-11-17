from decimal import Decimal
from typing import Any, Generic, Optional, TypeVar, List, Union
from pydantic.generics import GenericModel
from pydantic import BaseModel

from app.conf.config import settings

from .enums import Choices

DataType = TypeVar("DataType")


class IResponseBase(GenericModel, Generic[DataType]):
    message: Optional[str] = None
    errors: Optional[Any] = None
    data: Optional[DataType] = None

    class Config:
        json_encoders = {
            Choices: lambda x: {
                'value': x.value,
                'label': str(x.label),
            }
        }


class IPaginationDataBase(GenericModel, Generic[DataType]):
    count: Optional[int] = 0
    limit: Optional[int] = settings.PAGINATION_MAX_SIZE
    page: Optional[int] = 1
    rows: Optional[List[DataType]] = None


class IPaginationBase(GenericModel, Generic[DataType]):
    message: Optional[str] = ''
    errors: Optional[Any] = None
    data: Optional[IPaginationDataBase[DataType]] = None

    class Config:
        json_encoders = {
            Choices: lambda x: {
                'value': x.value,
                'label': str(x.label),
            }
        }


class MoneyBase(BaseModel):
    amount: Optional[Decimal] = None
    currency: Optional[str] = None

    class Config:
        orm_mode = True


class TaxedMoneyBase(BaseModel):
    currency: Optional[str] = None
    net: Optional[MoneyBase] = None
    gross: Optional[MoneyBase] = None
    tax: Optional[MoneyBase] = None

    class Config:
        orm_mode = True


class CommonsModel(BaseModel):
    limit: Optional[int] = settings.PAGINATION_MAX_SIZE
    offset: Optional[int] = 0
    page: Optional[int] = 1
    order_by: Optional[list] = []


class ChoiceBase(BaseModel):
    value: Optional[Union[str, int]] = None
    label: Optional[str] = None
