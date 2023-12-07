from pydantic.main import BaseModel
from pydantic.networks import AnyHttpUrl


class LinksList(BaseModel):
    links: list[AnyHttpUrl]


class Domains(BaseModel):
    domains: list[str]
    status: str
