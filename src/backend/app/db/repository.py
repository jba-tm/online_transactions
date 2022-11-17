from typing import Generic, List, Optional, Type, TypeVar, Union, Any, Dict, TYPE_CHECKING, Iterable
from uuid import UUID
from sqlalchemy import func, text, select
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.exc import NoResultFound
from sqlalchemy.engine.row import Row

from app.core.exceptions import DoesNotExist
from app.core.enums import Choices

from .models import Base

if TYPE_CHECKING:
    from sqlalchemy.orm import Session
    from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBaseSync(Generic[ModelType]):
    __slots__ = ('model',)

    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**


        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    def first(
            self,
            db: "Session",
            *,
            params: dict,
            options: Optional[Iterable] = (),
            expressions: Optional[Iterable] = (),
    ) -> Optional[ModelType]:
        """
        Soft retrieve obj
        :param db:
        :param params:
        :param options:
        :param expressions:
        :return:
        """
        return db.execute(
            select(self.model).options(*options).filter(*expressions).filter_by(**params)
        ).scalars().first()

    def create(self, db: "Session", *, obj_in: Union[dict, CreateSchemaType]) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in, custom_encoder={Choices: lambda x: x.value})
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def count(
            self, db: "Session", *,
            expressions: Optional[Iterable] = (),
            params: Optional[dict] = None,
    ) -> int:
        """

        :param db:
        :param expressions:
        :param params:
        :return:
        """
        if params is None:
            params = {}
        return db.execute(select(func.count(self.model.id)).filter(*expressions).filter_by(**params)).scalar_one()

    def exists(
            self, db: "Session", *,
            expressions: Optional[Iterable] = (),
            params: Optional[dict] = None,
    ) -> Any:
        """
        Check the item exist
        :param db:
        :param expressions:
        :param params:
        :return:
        """
        return db.execute(
            select(select(self.model).filter(*expressions).filter_by(**params).exists())
        ).scalar_one()

    def get_all(
            self,
            db: "Session",
            *,
            offset: Optional[int] = 0,
            limit: Optional[int] = 100,
            q: Optional[dict] = None,
            order_by: Optional[tuple] = (),

            options: Optional[Iterable] = (),
            expressions: Optional[Iterable] = (),
    ) -> List[ModelType]:
        """

        :param db: sqlalchemy.orm.Session
        :param offset:
        :param limit:
        :param q:
        :param order_by:
        :param expressions:
        :param options:
        :return:
        """
        if q is None:
            q = {}
        return db.execute(
            select(self.model).options(*options).filter(*expressions).filter_by(**q).order_by(*order_by).offset(
                offset).limit(limit)
        ).scalars().fetchall()

    def get_by_params(
            self, db: "Session",

            options: Optional[Iterable] = (),
            expressions: Optional[Iterable] = (),
            params: Optional[dict] = None, ) -> ModelType:
        """
        Retrieve items by params
        :param db:
        :param options:
        :param expressions:
        :param params:
        :return:
        """
        if params is None:
            params = {}
        result = db.execute(select(self.model).options(*options).filter(*expressions).filter_by(**params))

        try:
            return result.scalar_one()
        except NoResultFound:
            self.does_not_exist()

    def get(
            self,
            db: "Session",
            obj_id: Union[int, UUID],
            options: Optional[Iterable] = ()
    ) -> ModelType:
        """
        Retrieve obj, if does not exist raise exception
        :param db:
        :param obj_id:
        :param options:
        :return:
        """
        result = db.execute(select(self.model).options(*options).where(self.model.id == obj_id))

        try:
            return result.scalar_one()
        except NoResultFound:
            self.does_not_exist()

    @staticmethod
    def update(
            db: "Session",
            *,
            db_obj: ModelType,
            obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj, custom_encoder={Choices: lambda x: x.value})
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def does_not_exist(self) -> None:
        """
        @raise DoesNotExist
        """
        raise DoesNotExist(f'{self.model.__name__} - does not exist')


class CRUDBase(Generic[ModelType]):
    __slots__ = ('model',)

    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**


        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    async def count(
            self, async_db: "AsyncSession", *,
            expressions: Optional[Iterable] = (),
            params: Optional[dict] = None,
    ) -> int:
        """

        :param async_db:
        :param expressions:
        :param params:
        :return:
        """
        if params is None:
            params = {}
        query = await async_db.execute(select(func.count(self.model.id)).filter(*expressions).filter_by(**params))
        return query.scalar_one()

    async def exists(
            self, async_db: "AsyncSession", *,
            expressions: Optional[Iterable] = (),
            params: Optional[dict] = None,
    ) -> Any:
        """
        Check the item exist
        :param async_db:
        :param expressions:
        :param params:
        :return:
        """
        if params is None:
            params = {}
        query = await async_db.execute(select(select(self.model).filter(*expressions).filter_by(**params).exists()))
        return query.scalar_one()

    async def get_by_params(
            self, async_db: "AsyncSession",
            expressions: Optional[Iterable] = (),
            options: Optional[Iterable] = (),
            params: Optional[dict] = None, ) -> ModelType:
        """
        Retrieve items by params
        :param async_db:
        :param expressions:
        :param options:
        :param params:
        :return:
        """
        if params is None:
            params = {}
        select_q = select(self.model).options(*options).filter(*expressions).filter_by(**params)
        result = await async_db.execute(select_q)

        try:
            return result.scalar_one()
        except NoResultFound:
            self.does_not_exist()

    async def first(
            self,
            async_db: "AsyncSession",
            *,
            params: dict,
            expressions: Optional[Iterable] = (),
            options: Optional[Iterable] = (),
    ) -> Optional[ModelType]:
        """
        Soft retrieve obj
        :param async_db:
        :param params:
        :param expressions:
        :param options:
        :return:
        """
        select_q = select(self.model).options(*options).filter(*expressions).filter_by(**params)
        result = await async_db.execute(select_q)
        return result.scalars().first()

    async def get(
            self,
            async_db: "AsyncSession",
            obj_id: Union[int, UUID],
            options: Optional[Iterable] = (),
    ) -> ModelType:
        """
        Retrieve obj, if does not exist raise exception
        :param async_db:
        :param options:
        :param obj_id:
        :return:
        """
        result = await async_db.execute(select(self.model).options(*options).where(self.model.id == obj_id))

        try:
            return result.scalar_one()
        except NoResultFound:
            self.does_not_exist()

    async def get_all(
            self,
            async_db: "AsyncSession",
            *,
            offset: Optional[int] = 0,
            limit: Optional[int] = 100,
            q: Optional[dict] = None,
            order_by: Optional[Iterable] = (),
            options: Optional[Iterable] = (),
            expressions: Optional[Iterable] = (),
    ) -> List[ModelType]:
        """

        :param async_db:
        :param offset:
        :param limit:
        :param q:
        :param order_by:
        :param options:
        :param expressions:
        :return:
        """
        if q is None:
            q = {}
        result = await async_db.execute(
            select(self.model).options(*options).filter(*expressions).filter_by(**q).order_by(
                *order_by).offset(offset).limit(limit)
        )
        return result.scalars().fetchall()

    async def create(self, async_db: "AsyncSession", *, obj_in: Union[dict, CreateSchemaType]) -> ModelType:
        # obj_in_data = jsonable_encoder(obj_in, custom_encoder={Choices: lambda x: x.value})
        if isinstance(obj_in, dict):
            # obj_in_data = jsonable_encoder(obj_in, custom_encoder={Choices: lambda x: x.value})
            obj_in_data = obj_in
        else:
            obj_in_data = obj_in.dict()
        db_obj = self.model(**obj_in_data)  # type: ignore
        async_db.add(db_obj)
        await async_db.commit()
        await async_db.refresh(db_obj)
        return db_obj

    @staticmethod
    async def update(
            async_db: "AsyncSession",
            *,
            db_obj: ModelType,
            obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj, custom_encoder={Choices: lambda x: x.value})
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        async_db.add(db_obj)
        await async_db.commit()
        await async_db.refresh(db_obj)
        return db_obj

    @staticmethod
    async def delete(
            async_db: "AsyncSession", *,
            db_obj: Union[CreateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        Delete obj
        :param db_obj:
        :param async_db:
        :return:
        """
        await async_db.delete(db_obj)
        await async_db.commit()
        return db_obj

    def does_not_exist(self) -> None:
        """
        @raise DoesNotExist
        """
        raise DoesNotExist(f'{self.model.__name__} - does not exist')

    @staticmethod
    async def execute_raw_sql(async_db: "AsyncSession", *, sql_text: str, params: Optional[dict]) -> List[Row]:
        query = text(sql_text)
        return await async_db.execute(query, params=params)
