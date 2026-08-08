"""Sensor platform for service_entities."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, override

import voluptuous as vol
from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity_platform import async_get_platforms
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.util.async_ import run_callback_threadsafe

from .const import DOMAIN

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant, ServiceCall
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .data import ServiceEntitiesConfigEntry

LOGGER = logging.getLogger(__name__)


class SensorManager:
    """Sensor Manager."""

    def __init__(self, hass: HomeAssistant, async_add_entities: AddEntitiesCallback) -> None:
        """Create Manager."""
        self.hass = hass
        self.add_entities = async_add_entities
        self.entities = {}

    def handle_service_call(self, service: ServiceCall) -> None:
        """Direct service call to existing entity or create new."""
        LOGGER.debug("ServiceCall: %r", service.data)
        entity_id = service.data.get("entity_id")
        if entity_id not in self.entities:
            platforms = async_get_platforms(self.hass, DOMAIN)
            LOGGER.warning("PLATFORMS: %r", platforms)
            new_sensor = ServiceEntitiesSensor(
                self.hass,
                SensorEntityDescription(
                    key="service_entities",
                    name=entity_id,
                    icon="mdi:format-quote-close",
                ),
                entity_id,
            )
            platforms[0].add_entities([new_sensor])
            self.entities[entity_id] = new_sensor

        self.entities[entity_id].set(service.data)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ServiceEntitiesConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    LOGGER.debug("async_setup_entry")
    entry.sensor_manager = SensorManager(hass, async_add_entities)

    hass.services.async_register(
        DOMAIN,
        "set_entity",
        entry.sensor_manager.handle_service_call,
        schema=vol.Schema(
            {
                vol.Required("entity_id"): cv.entity_id,
                vol.Required("state"): cv.string,
                vol.Optional("name"): cv.string,
                vol.Optional("icon"): cv.icon,
                vol.Optional("unit_of_measurement"): cv.string,
                vol.Optional("attributes"): vol.Schema({}, extra=True),
            }
        ),
    )


class ServiceEntitiesSensor(RestoreEntity, SensorEntity):
    """service_entities Sensor class."""

    last_state = None

    def __init__(
        self,
        hass: HomeAssistant,
        entity_description: SensorEntityDescription,
        entity_id: str,
    ) -> None:
        """Initialize the sensor class."""
        LOGGER.debug("Sensor Init...")
        self.hass = hass
        self.entity_description = entity_description
        self.entity_id = entity_id

        self._attr_unique_id = f"service_entity__{entity_id}"

    @override
    async def async_added_to_hass(self) -> None:
        """Subscribe to the node and subnode event emitters."""
        await super().async_added_to_hass()
        if last_state := await self.async_get_last_state():
            self._attr_native_value = last_state.state
            self._attr_extra_state_attributes = last_state.attributes

    def set(self, state: Any) -> None:
        """Set sensor state."""
        LOGGER.debug("%s::set %r", self.entity_id, state)

        self._attr_native_value = state.get("state")
        self._attr_extra_state_attributes = state.get("attributes", None)

        self._attr_name = state.get("name", None)
        self._attr_icon = state.get("icon", None)
        self._attr_native_unit_of_measurement = state.get("unit_of_measurement", None)

        run_callback_threadsafe(self.hass.loop, self.async_write_ha_state).result()
