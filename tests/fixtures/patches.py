import pytest
from tortoise.exceptions import BaseORMException


@pytest.fixture
def patch_tortoise_resp_error(mocker):
    mocker.patch('core.database.models.Site.get_by_time_interval', side_effect=BaseORMException)
