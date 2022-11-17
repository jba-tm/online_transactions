from typing import Union, Optional, TYPE_CHECKING
from sqlalchemy import select
from fastapi.encoders import jsonable_encoder

from app.utils.security import lazy_jwt_settings
from app.db.repository import CRUDBase, CRUDBaseSync
from .schema import (UserBase, UserCreate)
from .models import User

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import Session


def convert_user_data(obj_in: Union[dict, UserBase]) -> dict:
    if isinstance(obj_in, dict):
        data = obj_in
    else:
        data = obj_in.dict(exclude_unset=True)

    if data.get('password'):
        hashed_password = lazy_jwt_settings.JWT_PASSWORD_HANDLER(data["password"])
        del data["password"]
        data["hashed_password"] = hashed_password
    return data


class CRUDUserSync(CRUDBaseSync[User]):
    def create(self, db: "Session", obj_in: Union[dict, UserCreate], **kwargs) -> User:
        data_in = convert_user_data(obj_in)
        data = jsonable_encoder(data_in)
        new_db_obj = User(**data)
        db.add(new_db_obj)
        db.commit()
        db.refresh(new_db_obj)
        return new_db_obj


class CRUDUser(CRUDBase[User]):
    @staticmethod
    async def get_by_email(async_db: "AsyncSession", *, email: str) -> Optional[User]:
        result = await async_db.execute(select(User).filter(User.email == email))
        return result.scalars().first()

    async def authenticate(self, async_db: "AsyncSession", *, email: str, password: str) -> Optional["User"]:
        user_db = await self.first(async_db, params={'email': email, })
        if not user_db:
            return None
        check_pass = lazy_jwt_settings.JWT_PASSWORD_VERIFY(password, user_db.hashed_password)
        if not check_pass:
            return None
        return user_db

    async def create(self, async_db: "AsyncSession", obj_in: Union[dict, UserCreate], **kwargs) -> User:
        data_in = convert_user_data(obj_in)
        db_obj = self.model()  # type: ignore

        for field in data_in:
            setattr(db_obj, field, data_in[field])

        async_db.add(db_obj)
        await async_db.commit()
        await async_db.refresh(db_obj)
        return db_obj


user_repo_sync = CRUDUserSync(User)
user_repo = CRUDUser(User)
