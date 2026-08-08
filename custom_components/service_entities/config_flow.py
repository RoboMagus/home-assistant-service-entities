"""Adds config flow for Blueprint."""

from __future__ import annotations

import logging

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_ID
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.loader import async_get_loaded_integration
from slugify import slugify

from .const import DOMAIN

LOGGER = logging.getLogger(__name__)

class BlueprintFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Blueprint."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            await self.async_set_unique_id(
                ## Do NOT use this in production code
                ## The unique_id should never be something that can change
                ## https://developers.home-assistant.io/docs/config_entries_config_flow_handler#unique-ids
                unique_id=slugify(user_input[CONF_ID])
            )
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=user_input[CONF_ID],
                data=user_input,
            )

        integration = async_get_loaded_integration(self.hass, DOMAIN)
        assert integration.documentation is not None, (  # noqa: S101
            "Integration documentation URL is not set in manifest.json"
        )

        return self.async_show_form(
            step_id="user",
            description_placeholders={
                "documentation_url": integration.documentation,
            },
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_ID,
                        default=(user_input or {}).get(CONF_ID, vol.UNDEFINED),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        ),
                    ),
                },
            ),
            errors=_errors,
        )