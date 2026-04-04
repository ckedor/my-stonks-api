from http import HTTPStatus

import pytest


@pytest.mark.asyncio
async def test_healthcheck_should_return_ok(client):
    response = await client.get('/hc')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'status': 'ok'}
