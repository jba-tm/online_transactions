from typing import TYPE_CHECKING
from loguru import logger

from app.conf.config import settings
from app.contrib.account.repository import user_repo, user_repo_sync
from app.contrib.account.schema import UserCreate

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import Session


def init_db_sync(db: "Session"):
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next line
    # Base.metadata.create_all(bind=engine)
    user_exist = user_repo_sync.exists(db, params={'email': settings.FIRST_SUPERUSER})
    if not user_exist:
        user_in = UserCreate(
            full_name='admin admin',
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_active=True,
            is_superuser=True,
            is_staff=True,
            user_type='admin',
        )
        user = user_repo_sync.create(db, obj_in=user_in)  # noqa: F841
        logger.info("User successfully created")


async def init_db(async_db: "AsyncSession") -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next line
    # Base.metadata.create_all(bind=engine)
    user_exist = await user_repo.exists(async_db, params={'email': settings.FIRST_SUPERUSER})

    if not user_exist:
        user_in = UserCreate(
            full_name='admin admin',
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
            is_staff=True,
            user_type='admin',
            is_active=True,
        )
        user = await user_repo.create(async_db, obj_in=user_in)  # noqa: F841
        logger.info("User successfully created")
