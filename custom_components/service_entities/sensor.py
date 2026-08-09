"""Sensor platform for service_entities."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, override

import voluptuous as vol
from homeassistant.exceptions import ServiceValidationError
from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity_platform import async_get_platforms
import homeassistant.helpers.entity_registry as er
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

    def __init__(self, hass: HomeAssistant, async_add_entities: AddEntitiesCallback, config_entry_id: str) -> None:
        """Create Manager."""
        self.hass = hass
        self.er = er.async_get(hass)
        self.add_entities = async_add_entities
        self.entities = {}

        entries = self.er.entities.get_entries_for_config_entry_id(config_entry_id)
        for e in entries:
            self.entities[e.entity_id] = ServiceEntitiesSensor(
                hass,
                SensorEntityDescription(
                    key=f"service_entity__{e.entity_id}",
                    name=e.name,
                    icon=e.icon,
                    device_class=e.device_class,
                    unit_of_measurement=e.unit_of_measurement,
                ),
                e.entity_id,
            )
        # Setup existing entries:
        async_add_entities(self.entities.values())

    def handle_service_call(self, service: ServiceCall) -> None:
        """Direct service call to existing entity or create new."""
        LOGGER.debug("ServiceCall: %r", service.data)
        entity_id = service.data.get("entity_id")
        if entity_id not in self.entities:
            if self.er.async_is_registered(entity_id):
                msg = f"Entity ID '{entity_id}' already exists and does not belong to the service_entities integration"
                raise ServiceValidationError(msg)

            new_sensor = ServiceEntitiesSensor(
                self.hass,
                SensorEntityDescription(
                    key=f"service_entity__{entity_id}",
                    name=service.data.get("name"),
                    icon=service.data.get("icon"),
                    unit_of_measurement=service.data.get("unit_of_measurement"),
                ),
                entity_id,
            )
            # Add entity using platform, as 'async_add_entities' task will have been destroyed after init stage
            platforms = async_get_platforms(self.hass, DOMAIN)
            platforms[0].add_entities([new_sensor])
            self.entities[entity_id] = new_sensor

        self.entities[entity_id].set(service.data)

    async def delete_entity(self, service: ServiceCall) -> None:
        """Delete entity."""
        LOGGER.debug("delete_entity: %r", service.data)
        entity_id = service.data.get("entity_id")
        if entity_id in self.entities:
            self.er.async_remove(entity_id)
            del self.entities[entity_id]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ServiceEntitiesConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    LOGGER.debug("async_setup_entry")
    entry.sensor_manager = SensorManager(hass, async_add_entities, entry.entry_id)

    hass.services.async_register(
        DOMAIN,
        "set_entity",
        entry.sensor_manager.handle_service_call,
        # Note: Name, Icon and UoM are ONLY used when creating new entities. They are ignored when updating existing ones!
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

    hass.services.async_register(
        DOMAIN,
        "delete_entity",
        entry.sensor_manager.delete_entity,
        schema=vol.Schema(
            {
                vol.Required("entity_id"): cv.entity_id,
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
        LOGGER.debug("%s init: %r", entity_id, entity_description)
        self.hass = hass
        self.entity_description = entity_description
        self.entity_id = entity_id

        self._attr_unique_id = f"service_entity__{entity_id}"

    @override
    async def async_added_to_hass(self) -> None:
        """Subscribe to the node and subnode event emitters."""
        await super().async_added_to_hass()
        if last_state := await self.async_get_last_state():
            LOGGER.debug("%s restore state: %r", self.entity_id, last_state)
            self._attr_native_value = last_state.state
            self._attr_extra_state_attributes = last_state.attributes

    def set(self, state: Any) -> None:
        """Set sensor state."""
        LOGGER.debug("%s set: %r", self.entity_id, state)

        self._attr_native_value = state.get("state")
        self._attr_extra_state_attributes = state.get("attributes", None)

        run_callback_threadsafe(self.hass.loop, self.async_write_ha_state).result()
