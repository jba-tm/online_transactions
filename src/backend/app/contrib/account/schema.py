from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, Dict, Any

from app.utils.translation import gettext as _


class UserBase(BaseModel):
    """ Base user model """
    full_name: Optional[str] = Field(None, max_length=255, alias='fullName')
    email: Optional[str] = Field(None)

    is_active: Optional[bool] = Field(True, alias='isActive')
    is_superuser: Optional[bool] = Field(False, alias='isSuperuser')
    email_confirmed_at: Optional[datetime] = Field(None, alias='emailConfirmedAt')
    language_code: Optional[str] = None

    password: Optional[str] = None

    class Config:
        allow_population_by_field_name = True


class UserCreate(UserBase):
    """ Creatable user fields"""
    id: Optional[UUID] = None
    full_name: str = Field(..., max_length=255, alias='fullName')
    password: Optional[str] = None

    class Config:
        allow_population_by_field_name = True


class UserInDBBase(UserBase):
    id: Optional[UUID] = None
    created_at: Optional[datetime] = Field(None, alias='createdAt')

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class User(UserInDBBase):
    pass


class UserVisible(BaseModel):
    id: Optional[UUID] = None
    full_name: Optional[str] = Field(None, max_length=255, alias='fullName')
    email: Optional[str] = Field(None)
    is_active: Optional[bool] = Field(True, alias='isActive')
    is_superuser: Optional[bool] = Field(False, alias='isSuperuser')

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: Optional[str] = None


class TokenPayload(BaseModel):
    user_id: UUID = Field(..., alias='user_id')
    iat: Optional[int] = None
    exp: Optional[int] = None

    # class Config:
    #     allow_population_by_field_name = True


class SignUp(BaseModel):
    full_name: str = Field(..., alias='fullName')
    email: EmailStr
    password_confirm: str = Field(..., alias='passwordConfirm')
    password: str

    @validator('password')
    def validate_password(cls, v: Optional[str], values: Dict[str, Any]):
        """
        Validate password
        :param v:
        :param values:
        :return:
        """
        password_confirm = values.get('password_confirm')
        if v != password_confirm:
            raise ValueError(_('Passwords does not match'))
        return v

    class Config:
        allow_population_by_field_name = True
