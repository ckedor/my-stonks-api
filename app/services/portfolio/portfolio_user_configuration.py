from fastapi import HTTPException

from app.api.portfolio.user_configuration.schemas import UserConfigurationUpdateRequest
from app.infrastructure.db.models.portfolio import (
    ConfigurationName,
    PortfolioUserConfiguration,
)
from app.infrastructure.db.repositories.portfolio import PortfolioRepository


async def get_user_configurations(session, portfolio_id: int):
    repo = PortfolioRepository(session)
    user_configurations = await repo.get(
        PortfolioUserConfiguration,
        by={'portfolio_id': portfolio_id}
    )

    config_names = await repo.get(ConfigurationName)
    name_options = [c.name for c in config_names]

    return {
        "configurations": [
            {
                "id": c.id,
                "portfolio_id": c.portfolio_id,
                "name": _get_name_by_id(config_names, c.configuration_name_id),
                "enabled": c.enabled,
                "config_data": c.config_data
            }
            for c in user_configurations
        ],
        "nameOptions": name_options
    }

def _get_name_by_id(config_names, config_name_id):
    for c in config_names:
        if c.id == config_name_id:
            return c.name
    return None

async def update_user_configuration(session, portfolio_id: int, user_configuration_request: UserConfigurationUpdateRequest):
    repo = PortfolioRepository(session)
    
    name = user_configuration_request.configuration
    enabled = user_configuration_request.enabled

    config_names = await repo.get(ConfigurationName, by={'name': name})
    if not config_names:
        raise HTTPException(status_code=400, detail="Invalid configuration name.")

    config_name = config_names[0]

    existing_configs = await repo.get(
        PortfolioUserConfiguration,
        by={
            "portfolio_id": portfolio_id,
            "configuration_name_id": config_name.id
        }
    )

    if not existing_configs:
        raise HTTPException(status_code=404, detail="Configuration not found.")

    config = existing_configs[0]
    config.enabled = enabled
    await repo.session.commit()

    return {"detail": "Configuration updated successfully"}