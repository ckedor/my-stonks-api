# app/modules/portfolio/service/portfolio_category_service.py
"""
Portfolio category service - handles custom category management.
"""

from typing import List

from app.infra.db.models.portfolio import CustomCategory, CustomCategoryAssignment
from app.infra.db.repositories.base_repository import SQLAlchemyRepository


class PortfolioCategoryService:
    def __init__(self, session):
        self.session = session
        self.repo = SQLAlchemyRepository(session)

    async def save_custom_categories(self, categories) -> None:
        for cat in categories:
            if cat.id is None:
                await self.repo.create(CustomCategory, cat.model_dump())
            else:
                await self.repo.update(CustomCategory, cat.model_dump())
        await self.session.commit()

    async def delete_custom_category(self, category_id: int) -> None:
        await self.repo.delete(CustomCategory, id=category_id)
        await self.session.commit()

    async def get_user_categories(self, portfolio_id: int):
        return await self.repo.get(CustomCategory, portfolio_id)

    async def assign_category_to_asset(self, payload):
        portfolio_id = payload.portfolio_id
        
        portfolio_categories = await self.repo.get(
            CustomCategory, by={'portfolio_id': portfolio_id}
        )

        portfolio_categories_ids = [cat.id for cat in portfolio_categories]

        custom_category_assignment = await self.repo.get(
            CustomCategoryAssignment,
            by={'custom_category_id__in': portfolio_categories_ids, 'asset_id': payload.asset_id},
            first=True,
        )
        if custom_category_assignment is None:
            await self.repo.create(
                CustomCategoryAssignment,
                {
                    'custom_category_id': payload.category_id,
                    'asset_id': payload.asset_id,
                },
            )
        else:
            await self.repo.update(
                CustomCategoryAssignment,
                {
                    'id': custom_category_assignment.id,
                    'custom_category_id': payload.category_id,
                    'asset_id': payload.asset_id,
                },
            )
        await self.session.commit()
