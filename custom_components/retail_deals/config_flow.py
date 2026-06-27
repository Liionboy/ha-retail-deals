"""Config flow for Retail Deals Romania."""
import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
    DOMAIN, CONF_STORES, CONF_TOP, CONF_MIN_DISCOUNT,
    CONF_SCAN_INTERVAL, DEFAULT_STORES, DEFAULT_TOP,
    DEFAULT_MIN_DISCOUNT, DEFAULT_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

STORE_OPTIONS = ["auchan", "kaufland", "lidl", "carrefour"]

DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_STORES, default=DEFAULT_STORES): vol.All(
        vol.Coerce(list),
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
                stores = user_input.get(CONF_STORES, DEFAULT_STORES)
                if isinstance(stores, str):
                    stores = [s.strip() for s in stores.split(",")]

                valid_stores = [s for s in stores if s in STORE_OPTIONS]
                if not valid_stores:
                    errors["base"] = "no_stores"
                else:
                    user_input[CONF_STORES] = valid_stores
                    return self.async_create_entry(
                        title="Retail Deals Romania",
                        data=user_input,
                    )
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            errors=errors,
        )
