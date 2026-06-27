"""Sensor platform for Retail Deals Romania."""
import logging
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
    SensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN, STORES, CONF_STORES, CONF_TOP,
    DEFAULT_STORES, DEFAULT_TOP,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    stores = entry.data.get(CONF_STORES, DEFAULT_STORES)
    top = entry.data.get(CONF_TOP, DEFAULT_TOP)

    entities = []

    # Main summary sensor
    entities.append(RetailDealsSummarySensor(coordinator, entry))

    # Top deal sensor (best overall)
    entities.append(RetailDealsTopSensor(coordinator, entry))

    # Per-store sensors
    for store_id in stores:
        entities.append(RetailDealsStoreSensor(coordinator, entry, store_id))

    # Individual deal sensors (top N)
    for i in range(min(top, 10)):
        entities.append(RetailDealsItemSensor(coordinator, entry, i))

    async_add_entities(entities)


class RetailDealsBaseSensor(CoordinatorEntity, SensorEntity):
    """Base class for retail deals sensors."""

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry

    @property
    def device_info(self) -> dict:
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": "Retail Deals Romania",
            "manufacturer": "Jarvis",
            "model": "Deals Collector",
            "sw_version": "1.0.0",
        }


class RetailDealsSummarySensor(RetailDealsBaseSensor):
    """Main summary sensor showing total deals count."""

    _attr_name = "Retail Deals Summary"
    _attr_icon = "mdi:shopping"
    _attr_native_unit_of_measurement = "oferte"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_summary"

    @property
    def native_value(self) -> int:
        data = self.coordinator.data or {}
        return data.get("total_deals", 0)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data or {}
        return {
            "by_store": data.get("by_store", {}),
            "last_update": data.get("last_update", ""),
            "best_discount": data.get("best_discount", 0),
            "best_product": data.get("best_product", ""),
            "best_store": data.get("best_store", ""),
        }


class RetailDealsTopSensor(RetailDealsBaseSensor):
    """Sensor showing the best deal."""

    _attr_name = "Retail Deals Best"
    _attr_icon = "mdi:tag-heart"
    _attr_native_unit_of_measurement = "%"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_top"

    @property
    def native_value(self) -> float:
        data = self.coordinator.data or {}
        return data.get("best_discount", 0)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data or {}
        deals = data.get("deals", [])
        if not deals:
            return {}
        best = deals[0]
        return {
            "product": best.get("product", ""),
            "store": best.get("store", ""),
            "price_old": best.get("price_old", 0),
            "price_new": best.get("price_new", 0),
            "savings": best.get("savings", 0),
            "url": best.get("url", ""),
        }


class RetailDealsStoreSensor(RetailDealsBaseSensor):
    """Sensor for a specific store."""

    def __init__(self, coordinator, entry, store_id: str):
        super().__init__(coordinator, entry)
        self._store_id = store_id
        store_info = STORES.get(store_id, {})
        self._attr_name = f"Deals {store_info.get('name', store_id)}"
        self._attr_icon = store_info.get("icon", "mdi:store")
        self._attr_native_unit_of_measurement = "oferte"
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_{store_id}"

    @property
    def native_value(self) -> int:
        data = self.coordinator.data or {}
        by_store = data.get("by_store", {})
        return by_store.get(self._store_id, {}).get("count", 0)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data or {}
        by_store = data.get("by_store", {})
        store_data = by_store.get(self._store_id, {})
        return {
            "avg_discount": store_data.get("avg_discount", 0),
            "best_discount": store_data.get("best_discount", 0),
            "best_product": store_data.get("best_product", ""),
        }


class RetailDealsItemSensor(RetailDealsBaseSensor):
    """Sensor for a specific deal (top N)."""

    def __init__(self, coordinator, entry, index: int):
        super().__init__(coordinator, entry)
        self._index = index
        self._attr_name = f"Retail Deal #{index + 1}"
        self._attr_icon = "mdi:tag-outline"
        self._attr_native_unit_of_measurement = "%"
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_deal_{index}"

    @property
    def native_value(self) -> float:
        data = self.coordinator.data or {}
        deals = data.get("deals", [])
        if self._index < len(deals):
            return deals[self._index].get("discount_pct", 0)
        return 0

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data or {}
        deals = data.get("deals", [])
        if self._index < len(deals):
            d = deals[self._index]
            return {
                "product": d.get("product", ""),
                "store": d.get("store", ""),
                "price_old": d.get("price_old", 0),
                "price_new": d.get("price_new", 0),
                "savings": d.get("savings", 0),
                "url": d.get("url", ""),
            }
        return {}
