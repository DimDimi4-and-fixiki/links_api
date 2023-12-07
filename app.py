import logging

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.responses import RedirectResponse

from config import APPLICATION_NAME

log = logging.getLogger('app')


application = FastAPI(
    title=APPLICATION_NAME,
    openapi_url='/api/openapi.json',
)


@application.get('/ping')
async def ping() -> str:
    return 'pong'


@application.get('/', include_in_schema=False)
async def redirect_to_docs() -> RedirectResponse:
    response = RedirectResponse(url='/docs')
    return response


@application.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(status_code=400, content={'status': f'Validation error: {str(exc)}'})


def build_app() -> FastAPI:
    from api.v1.routes import api_v1_router

    # include routers
    application.include_router(api_v1_router)

    return application
