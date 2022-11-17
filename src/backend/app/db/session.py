from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.conf.config import settings

async_engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True, echo=False)

db_uri = settings.SQLALCHEMY_DATABASE_URI.replace('+asyncpg', '')
engine = create_engine(db_uri, pool_pre_ping=True, echo=False)


SessionLocal = sessionmaker(
    expire_on_commit=True,
    autocommit=False,
    autoflush=False,
    # twophase=True,
    bind=engine
)

AsyncSessionLocal = sessionmaker(
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
    bind=async_engine,
    future=True,
)

test_db_uri = settings.SQLALCHEMY_TEST_DATABASE_URI.replace('+asyncpg', '')
testing_engine = create_engine(test_db_uri, pool_pre_ping=True)

test_async_engine = create_async_engine(
    settings.SQLALCHEMY_TEST_DATABASE_URI, pool_pre_ping=True, echo=False,
)
TestingSessionLocal = sessionmaker(
    expire_on_commit=True,
    # twophase=True,
    autoflush=False,
    autocommit=False,
    bind=testing_engine
)

AsyncTestingSessionLocal = sessionmaker(
    class_=AsyncSession,
    expire_on_commit=False,
    # twophase=True,
    autoflush=False,
    autocommit=False,
    bind=test_async_engine,
    future=True,
)
