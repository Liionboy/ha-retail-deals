"""The Retail Deals Romania integration."""
import asyncio
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN, CONF_STORES, CONF_TOP, CONF_MIN_DISCOUNT,
    CONF_SCAN_INTERVAL, DEFAULT_STORES, DEFAULT_TOP,
    DEFAULT_MIN_DISCOUNT, DEFAULT_SCAN_INTERVAL,
)
from .collector import collect_all_deals

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Retail Deals from a config entry."""
    stores = entry.data.get(CONF_STORES, DEFAULT_STORES)
    top = entry.data.get(CONF_TOP, DEFAULT_TOP)
    min_discount = entry.data.get(CONF_MIN_DISCOUNT, DEFAULT_MIN_DISCOUNT)
    scan_interval = entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

    coordinator = RetailDealsCoordinator(
        hass, stores=stores, top=top,
        min_discount=min_discount,
        scan_interval_minutes=scan_interval,
    )

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register update listener for options changes
    entry.async_on_unload(entry.add_update_listener(async_update_options))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


class RetailDealsCoordinator(DataUpdateCoordinator):
    """Coordinator to fetch retail deals data."""

    def __init__(
        self, hass: HomeAssistant, *,
        stores: list[str], top: int,
        min_discount: float, scan_interval_minutes: int,
    ) -> None:
        super().__init__(
            hass, _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=scan_interval_minutes),
        )
        self.stores = stores
        self.top = top
        self.min_discount = min_discount

    async def _async_update_data(self) -> dict:
        """Fetch data from retail stores."""
        try:
            data = await asyncio.get_event_loop().run_in_executor(
                None, collect_all_deals,
                self.stores, self.top, self.min_discount,
            )
            return data
        except Exception as err:
            raise UpdateFailed(f"Error fetching deals: {err}") from err
