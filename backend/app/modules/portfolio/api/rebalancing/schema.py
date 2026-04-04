from typing import List

from pydantic import BaseModel


class AssetTargetRequest(BaseModel):
    asset_id: int
    target_percentage: float


class CategoryTargetRequest(BaseModel):
    category_id: int
    target_percentage: float
    assets: List[AssetTargetRequest]


class SaveTargetsRequest(BaseModel):
    portfolio_id: int
    categories: List[CategoryTargetRequest]


class AssetRebalancingEntry(BaseModel):
    asset_id: int
    ticker: str
    name: str
    category: str
    category_id: int
    current_value: float
    current_pct_in_category: float
    target_pct_in_category: float | None
    target_value: float | None
    diff_pct: float | None
    diff_value: float | None


class CategoryRebalancingEntry(BaseModel):
    category_id: int
    category_name: str
    color: str
    current_value: float
    current_pct: float
    target_pct: float | None
    target_value: float | None
    diff_pct: float | None
    diff_value: float | None
    assets: List[AssetRebalancingEntry]


class RebalancingResponse(BaseModel):
    portfolio_id: int
    total_value: float
    categories: List[CategoryRebalancingEntry]
