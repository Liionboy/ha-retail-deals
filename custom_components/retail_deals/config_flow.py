"""Config flow for Retail Deals Romania."""
import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import (
    DOMAIN, CONF_STORES, CONF_TOP, CONF_MIN_DISCOUNT,
    CONF_SCAN_INTERVAL, DEFAULT_STORES, DEFAULT_TOP,
    DEFAULT_MIN_DISCOUNT, DEFAULT_SCAN_INTERVAL, STORES,
)

_LOGGER = logging.getLogger(__name__)

STORE_OPTIONS = {
    "auchan": "Auchan",
    "kaufland": "Kaufland",
    "lidl": "Lidl",
    "carrefour": "Carrefour",
}

STEP_USER_DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_STORES, default=DEFAULT_STORES): vol.All(
        vol.Coerce(list), [vol.In(STORE_OPTIONS)]
    ),
    vol.Required(CONF_TOP, default=DEFAULT_TOP): vol.All(
        vol.Coerce(int), vol.Range(min=5, max=50)
    ),
    vol.Required(CONF_MIN_DISCOUNT, default=DEFAULT_MIN_DISCOUNT): vol.All(
        vol.Coerce(int), vol.Range(min=5, max=80)
    ),
    vol.Required(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
        vol.Coerce(int), vol.Range(min=60, max=1440)
    ),
})


class RetailDealsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Retail Deals."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                # Validate stores
                stores = user_input.get(CONF_STORES, DEFAULT_STORES)
                if not stores:
                    errors["base"] = "no_stores"
                    return self.async_show_form(
                        step_id="user",
                        data_schema=STEP_USER_DATA_SCHEMA,
                        errors=errors,
                    )

                return self.async_create_entry(
                    title="Retail Deals Romania",
                    data=user_input,
                )

            except Exception as err:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
