import pytest
import asyncio
import sys

from typing import Any, Generator, TYPE_CHECKING, Callable, Optional
from httpx import AsyncClient

from asgi_lifespan import LifespanManager
from typing import Iterator

from app.conf.config import settings
from app.main import app
from app.contrib.account.repository import user_repo, user_repo_sync
from app.contrib.wallet.repository import wallet_repo
from app.utils.security import lazy_jwt_settings

if TYPE_CHECKING:
    from faker import Faker
    from fastapi import FastAPI
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import Session
    from app.contrib.account.models import User
    from app.contrib.wallet.models import Wallet


def get_current_event_loop() -> Iterator[asyncio.AbstractEventLoop]:
    """Yield an event loop.
    This is necessary because pytest-asyncio needs an event loop with a with an equal or higher
    pytest fixture scope as any of the async fixtures. And remember, pytest-asyncio is what allows us
    to have async pytest fixtures.
    """
    if sys.platform.startswith("win") and sys.version_info[:2] >= (3, 8):
        # Avoid "RuntimeError: Event loop is closed" on Windows when tearing down tests
        # https://github.com/encode/httpx/issues/914
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:

        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


event_loop = pytest.fixture(fixture_function=get_current_event_loop, scope='session', name="event_loop")


@pytest.fixture(scope='session')
def celery_config():
    return {
        'broker_url': 'memory://',
        'result_backend': 'redis://'
    }


@pytest.fixture(scope='session')
def celery_includes():
    return [
        'app.contrib.auth.tasks',
        'app.contrib.order.tasks',
    ]


@pytest.fixture(scope='session')
def use_celery_app_trap():
    return True


@pytest.fixture
async def app_settings() -> Any:
    return settings


@pytest.fixture
def db():
    """
    Creates a fresh sqlalchemy session for each test that operates in a
    transaction. The transaction is rolled back at the end of each test ensuring
    a clean state.
    """
    from app.db.session import TestingSessionLocal, testing_engine
    from app.db.init_db import init_db_sync
    from app.db.models import PlainBase
    from sqlalchemy_utils import database_exists, create_database, drop_database
    if not database_exists(testing_engine.url):
        create_database(testing_engine.url)

    # connect to the database
    is_echo = testing_engine.echo
    testing_engine.echo = False
    PlainBase.metadata.create_all(bind=testing_engine)
    testing_engine.echo = is_echo

    # connect to the database
    connection = testing_engine.connect()
    # begin a non-ORM transaction
    transaction = connection.begin()
    # bind an individual Session to the connection
    session = TestingSessionLocal(bind=connection)
    init_db_sync(session)
    yield session  # use the session in tests.
    session.close()
    # rollback - everything that happened with the
    # Session above (including calls to commit())
    # is rolled back.
    transaction.rollback()
    # return connection to the Engine
    connection.close()
    if database_exists(testing_engine.url):
        drop_database(testing_engine.url)


@pytest.fixture(scope="session")
async def async_db():
    from app.db.session import AsyncTestingSessionLocal, test_async_engine
    from app.db.init_db import init_db
    from app.db.models import PlainBase
    from sqlalchemy_utils import database_exists, create_database, drop_database

    database_url = test_async_engine.url.render_as_string(hide_password=False).replace('+asyncpg', '')
    if not database_exists(database_url):
        create_database(database_url)
    # connect to the database
    is_echo = test_async_engine.echo
    test_async_engine.echo = False
    async with test_async_engine.begin() as conn:
        await conn.run_sync(PlainBase.metadata.create_all)  # Create the tables.
    test_async_engine.echo = is_echo

    async with test_async_engine.connect() as conn:
        async with AsyncTestingSessionLocal(bind=conn, ) as session:
            await init_db(session)
            yield session

        # rollback - everything that happened with the
        # Session above (including calls to commit())
        # is rolled back.
        await conn.rollback()

    # for AsyncEngine created in function scope, close and
    # clean-up pooled connections
    await test_async_engine.dispose()

    # Drop test database

    if database_exists(database_url):
        drop_database(database_url)


@pytest.fixture
def admin_sync(db: "Session", ) -> "User":
    user = user_repo_sync.first(db, params={'email': settings.FIRST_SUPERUSER})
    if user:
        return user
    return user_repo_sync.create(
        db,
        obj_in={
            'email': settings.FIRST_SUPERUSER,
            'full_name': 'Admin',
            'password': settings.FIRST_SUPERUSER_PASSWORD,
            'is_active': True,
            'is_superuser': True,
        }
    )


@pytest.fixture
async def get_admin(async_db: "AsyncSession", faker: "Faker") -> Callable:
    async def func() -> "User":
        user = await user_repo.first(async_db, params={'email': settings.FIRST_SUPERUSER})
        if not user:
            user = await user_repo.create(
                async_db,
                obj_in={
                    'email': settings.FIRST_SUPERUSER,
                    'full_name': 'Admin Admin',
                    'password': settings.FIRST_SUPERUSER_PASSWORD,
                    'is_active': True,
                    'is_superuser': True,
                }
            )
        return user

    return func


@pytest.fixture
async def get_simple_user(async_db: "AsyncSession", faker: "Faker") -> "Callable":
    async def func(params: Optional[dict] = None) -> "User":
        if params is None:
            params = {}
        email = params['email'] if params.get('email') else faker.unique.email()
        user = await user_repo.first(async_db, params={'email': email})
        if not user:
            user = await user_repo.create(
                async_db,
                obj_in={
                    'email': email,
                    'full_name': 'Simple User',
                    'password': 'secret',
                    'is_active': True,
                    'is_superuser': False,
                    **params,
                }
            )
        return user

    return func


@pytest.fixture
async def admin_token_headers(get_admin: Callable) -> dict:
    """
    Retrieve admin token auth header
    :param get_admin:
    :return: dict
    """
    admin = await get_admin()
    payload = lazy_jwt_settings.JWT_PAYLOAD_HANDLER(
        {
            'user_id': str(admin.id),
            'aud': lazy_jwt_settings.JWT_ADMIN_AUDIENCE,
        },
    )
    jwt_token = lazy_jwt_settings.JWT_ENCODE_HANDLER(payload)

    return {
        'Authorization': f'Bearer {jwt_token}'
    }


@pytest.fixture
def get_token_headers():
    def func(user: "User", audience: str):
        payload = lazy_jwt_settings.JWT_PAYLOAD_HANDLER(
            {
                'user_id': str(user.id),
                'aud': audience,
            },
        )
        jwt_token = lazy_jwt_settings.JWT_ENCODE_HANDLER(payload)

        return {
            'Authorization': f'Bearer {jwt_token}'
        }

    return func


@pytest.fixture(autouse=True)
async def application() -> Generator["FastAPI", Any, None]:
    yield app


@pytest.fixture
async def async_client(application: "FastAPI", async_db: "AsyncSession") -> Generator[AsyncClient, Any, None]:
    """
    Create a new FastAPI TestClient that uses the `db` fixture to override
    the `get_db` dependency that is injected into routes.
    """
    from app.routers import dependency

    async def _get_test_db():
        return async_db

    application.dependency_overrides[dependency.get_async_db] = _get_test_db

    async with LifespanManager(application):
        async with AsyncClient(app=application, base_url="http://test") as _client:
            try:
                yield _client
            except Exception as exc:  # pylint: disable=broad-except
                print(exc)


@pytest.fixture
async def get_wallet(async_db: "AsyncSession"):
    async def func(user: "User", params: Optional[dict] = None) -> "Wallet":
        if params is None:
            params = {}
        currency = params['currency'] if params.get('currency') else settings.DEFAULT_CURRENCY_CODE
        wallet = await wallet_repo.first(async_db, params={'currency': currency, 'user_id': user.id})
        if not wallet:
            wallet = await wallet_repo.create(
                async_db,
                obj_in={
                    'user_id': user.id,
                    'currency': currency,
                    'total_amount': params['total_amount'] if params.get('total_amount') else 10000,
                    'is_active': params['is_active'] if params.get('is_active') else True,
                }
            )
        return wallet
    return func
