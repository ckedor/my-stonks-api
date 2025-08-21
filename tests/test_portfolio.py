from http import HTTPStatus

import pytest

from app.infrastructure.db.models.portfolio import CustomCategory, Portfolio
from app.users.models import User


@pytest.mark.asyncio
async def test_get_portfolios(client, db):
    user = db.query(User).filter_by(id=1).first()
    portfolio = Portfolio(name='Principal', user_id=user.id)
    db.add(portfolio)
    db.flush()
    category = CustomCategory(name='Categoria Teste', portfolio_id=portfolio.id)
    db.add(category)
    db.commit()

    response = await client.get('/portfolio/portfolios')

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    portfolio = data[0]
    assert isinstance(data, list)
    assert len(data) > 0
    assert portfolio['user_id'] == 1
    assert portfolio['name'] == 'Principal'
