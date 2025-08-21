from fastapi import HTTPException

from app.api.portfolio.portfolio.schemas import (
    CreatePortfolioRequest,
    UpdatePortfolioRequest,
)
from app.infrastructure.db.models.portfolio import (
    CustomCategory,
    CustomCategoryAssignment,
    Dividend,
    Portfolio,
    Position,
    Transaction,
)
from app.infrastructure.db.repositories.portfolio import PortfolioRepository


async def create_portfolio(session, portfolio: CreatePortfolioRequest, user_id: int):
    # TODO: Unit of Work Pattern
    repo = PortfolioRepository(session)
    id_list = await repo.create(Portfolio, {'name': portfolio.name, 'user_id': user_id})
    user_categories = portfolio.user_categories
    if not id_list:
        raise HTTPException(status_code=400, detail='Erro ao criar portfolio')
    categories = [
        CustomCategory(
            **cat.model_dump(exclude={'portfolio_id'}),
            portfolio_id=id_list[0],
        )
        for cat in user_categories
    ]
    await repo.create(CustomCategory, categories)

    portfolio_id = id_list[0]
    return portfolio_id

async def list_user_portfolios(session, user_id: int) -> Portfolio:
    repo = PortfolioRepository(session)
    portfolios = await repo.get_user_portfolios(user_id)
    return portfolios

async def update_portfolio(session, portfolio: UpdatePortfolioRequest) -> None:    
    async with session.begin():
        repo = PortfolioRepository(session)
        portfolio = await repo.get(Portfolio, portfolio.id)
        if not portfolio:
            raise HTTPException(status_code=404, detail='Portfolio não encontrado')

        await repo.update(
            Portfolio,
            portfolio.model_dump(exclude={'user_categories'}),
        )

        for cat in portfolio.user_categories:
            if cat.id is None:
                await repo.create(CustomCategory, cat.model_dump())
            else:
                await repo.update(CustomCategory, cat.model_dump())

async def delete_portfolio(session, portfolio_id: int) -> None:
    async with session.begin():
        repo = PortfolioRepository(session)
        portfolio = await repo.get(Portfolio, portfolio_id)
        if not portfolio:
            raise HTTPException(status_code=404, detail='Portfolio não encontrado')

        custom_categories = await repo.get(
            CustomCategory, by={'portfolio_id': portfolio_id}
        )   
        for custom_category in custom_categories:
            await repo.delete(CustomCategoryAssignment, by={'custom_category_id': custom_category.id})
        await repo.delete(CustomCategory, by={'portfolio_id': portfolio_id})
        await repo.delete(Position, by={'portfolio_id': portfolio_id})
        await repo.delete(Transaction, by={'portfolio_id': portfolio_id})
        await repo.delete(Dividend, by={'portfolio_id': portfolio_id})
        await repo.delete(Portfolio, portfolio_id)
