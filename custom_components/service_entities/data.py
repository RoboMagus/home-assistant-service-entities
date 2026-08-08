"""Custom types for service_entities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import ServiceEntitiesApiClient
    from .coordinator import BlueprintDataUpdateCoordinator


type ServiceEntitiesConfigEntry = ConfigEntry[ServiceEntitiesData]


@dataclass
class ServiceEntitiesData:
    """Data for the Blueprint integration."""

    client: ServiceEntitiesApiClient
    coordinator: BlueprintDataUpdateCoordinator
    integration: Integration
