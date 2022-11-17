import aioredis
import uvicorn
import sentry_sdk

from typing import Optional
from fastapi import HTTPException, Depends, APIRouter
from fastapi.responses import ORJSONResponse
from starlette.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.conf.config import settings
from app.core.app import FastAPI
from app.routers.dependency import get_language
from app.utils.translation import (
    LANGUAGE_COOKIE,
    LANGUAGE_HEADER,
    LocaleFromCookieMiddleware,
    LocaleFromHeaderMiddleware,
    load_gettext_translations,
    LocaleFromQueryParamsMiddleware,
)
from app.routers.api import api
from app.routers.router import router

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production,
    traces_sample_rate=1.0,
)


def get_application(
        app_api: APIRouter,
        app_router: APIRouter,
        root_path: Optional[str] = None,
        root_path_in_servers: Optional[bool] = False,
) -> FastAPI:
    load_gettext_translations(directory=settings.LOCALE.get('DIR', 'app/locale'), domain='messages')

    application = FastAPI(
        dependencies=[Depends(get_language)],
        default_response_class=ORJSONResponse,
        title=settings.PROJECT_NAME,
        debug=settings.DEBUG,
        version=settings.VERSION,
        middleware=[
            # Middleware(
            #     LocaleFromHeaderMiddleware,
            #     language_header=LANGUAGE_HEADER,
            #     default_code=settings.LANGUAGE_CODE
            # ),
            # Middleware(
            #     LocaleFromCookieMiddleware,
            #     language_cookie=LANGUAGE_COOKIE,
            #     default_code=settings.LANGUAGE_CODE
            # ),
            Middleware(LocaleFromQueryParamsMiddleware, default_code=settings.LANGUAGE_CODE),

        ],
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        root_path=root_path,
        root_path_in_servers=root_path_in_servers,

    )

    # Set all CORS enabled origins
    if settings.BACKEND_CORS_ORIGINS:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    else:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=['*'],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    @application.on_event('startup')
    async def startup():
        # configure_mappers()
        aioredis_instance = aioredis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            encoding="utf8",
        )

        await application.configure(
            aioredis_instance=aioredis_instance,
        )

    application.mount("/static", StaticFiles(directory="static", html=True), name="static")

    application.include_router(app_api, prefix=settings.API_V1_STR)
    application.include_router(app_router, )

    return application


app = get_application(
    app_api=api,
    root_path=settings.ROOT_PATH,
    root_path_in_servers=settings.ROOT_PATH_IN_SERVERS,
    app_router=router,
)
