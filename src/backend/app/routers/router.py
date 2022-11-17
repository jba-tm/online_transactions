from fastapi import APIRouter
from fastapi.responses import FileResponse

from app.utils.translation import gettext as _

router = APIRouter()


@router.get('/favicon.ico', response_class=FileResponse, name='favicon', tags=['favicon'])
async def favicon() -> FileResponse:
    return FileResponse('static/images/logo/favicon.ico')


@router.get("/sentry-debug/", name='sentry-debug', tags=['sentry-debug'])
async def trigger_error():
    division_by_zero = 1 / 0


@router.get('/', name='main', tags=['main'])
def main():
    return _('Hello')
