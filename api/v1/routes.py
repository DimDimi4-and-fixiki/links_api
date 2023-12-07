import time

import tortoise.exceptions
from fastapi import APIRouter
from pydantic.networks import AnyHttpUrl

from api.v1.schemas import Domains, LinksList, Status
from core.database.models import Site

api_v1_router = APIRouter(
    prefix='/api/v1',
    tags=['api_v1'],
    dependencies=[],
)


@api_v1_router.get('/ping')
async def ping() -> str:
    return 'pong from service'


@api_v1_router.post('/visited_links/', response_model=Status)
async def visited_links(links: LinksList):
    current_time = time.time()

    for link in links.links:
        await Site.create(visited_at=current_time, url=link.unicode_string())

    return Status(status='ok')


@api_v1_router.get('/visited_domains/', response_model=Domains)
async def visited_domains(from_time: int, to_time: int):
    try:
        domains = []
        sites = await Site.get_by_time_interval(from_time=from_time, to_time=to_time)

        for site in sites:
            domains.append(AnyHttpUrl(site.url).unicode_host())
        return Domains(domains=domains, status='ok')

    except (tortoise.exceptions.DBConnectionError, tortoise.exceptions.BaseORMException) as e:
        return Domains(domains=[], status=f'error {e}')
