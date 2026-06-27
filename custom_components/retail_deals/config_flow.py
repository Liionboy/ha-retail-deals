"""Config flow for Retail Deals Romania."""
import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
)

from .const import (
    DOMAIN, CONF_STORES, CONF_TOP, CONF_MIN_DISCOUNT,
    CONF_SCAN_INTERVAL, DEFAULT_STORES, DEFAULT_TOP,
    DEFAULT_MIN_DISCOUNT, DEFAULT_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

STORE_OPTIONS = [
    {"value": "auchan", "label": "Auchan"},
    {"value": "kaufland", "label": "Kaufland"},
    {"value": "lidl", "label": "Lidl"},
    {"value": "carrefour", "label": "Carrefour"},
]

DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_STORES, default=DEFAULT_STORES): SelectSelector(
        SelectSelectorConfig(
            options=STORE_OPTIONS,
            multiple=True,
            mode=SelectSelectorMode.LIST,
        )
    ),
    vol.Required(CONF_TOP, default=DEFAULT_TOP): NumberSelector(
        NumberSelectorConfig(min=5, max=50, mode=NumberSelectorMode.BOX)
    ),
    vol.Required(CONF_MIN_DISCOUNT, default=DEFAULT_MIN_DISCOUNT): NumberSelector(
        NumberSelectorConfig(min=5, max=80, mode=NumberSelectorMode.BOX, unit_of_measurement="%")
    ),
    vol.Required(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): NumberSelector(
        NumberSelectorConfig(min=60, max=1440, mode=NumberSelectorMode.BOX, unit_of_measurement="min")
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
                if not stores:
                    errors["base"] = "no_stores"
                else:
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
