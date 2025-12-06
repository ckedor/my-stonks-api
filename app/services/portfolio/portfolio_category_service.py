from typing import List

from app.infra.db.models.portfolio import CustomCategory, CustomCategoryAssignment
from app.infra.db.repositories.base_repository import DatabaseRepository


async def save_custom_categories(session, categories) -> None:
    
    repo = DatabaseRepository(session)
    for cat in categories:
        if cat.id is None:
            await repo.create(CustomCategory, cat.model_dump())
        else:
            await repo.update(CustomCategory, cat.model_dump())
    await session.commit()

async def delete_custom_category(session, category_id: int) -> None:
    repo = DatabaseRepository(session)
    await repo.delete(CustomCategory, id=category_id)
    await session.commit()

async def get_user_categories(session, portfolio_id: int):
    repo = DatabaseRepository(session)
    return await repo.get(CustomCategory, portfolio_id)

async def assign_category_to_asset(session, payload):
    portfolio_id = payload.portfolio_id
    
    repo = DatabaseRepository(session)
    portfolio_categories = await repo.get(
        CustomCategory, by={'portfolio_id': portfolio_id}
    )

    portfolio_categories_ids = [cat.id for cat in portfolio_categories]

    custom_category_assignment = await repo.get(
        CustomCategoryAssignment,
        by={'custom_category_id__in': portfolio_categories_ids, 'asset_id': payload.asset_id},
        first=True,
    )
    if custom_category_assignment is None:
        await repo.create(
            CustomCategoryAssignment,
            {
                'custom_category_id': payload.category_id,
                'asset_id': payload.asset_id,
            },
        )
    else:
        await repo.update(
            CustomCategoryAssignment,
            {
                'id': custom_category_assignment.id,
                'custom_category_id': payload.category_id,
                'asset_id': payload.asset_id,
            },
        )
    await session.commit()
