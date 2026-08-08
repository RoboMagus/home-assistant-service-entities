"""Custom types for service_entities."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry

type ServiceEntitiesConfigEntry = ConfigEntry[dict[str, Any]]
