"""Sensor platform for Retail Deals Romania."""
import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
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

    # Main summary sensor — all deals as attributes
    entities.append(RetailDealsSummarySensor(coordinator, entry))

    # Per-store sensors
    for store_id in stores:
        entities.append(RetailDealsStoreSensor(coordinator, entry, store_id))

    # Individual deal sensors (top 10) — product name as state
    for i in range(min(int(top), 10)):
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
    """Main summary sensor — state = total deals, attributes = all deals list."""

    _attr_name = "Retail Deals Summary"
    _attr_icon = "mdi:shopping"

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
        deals = data.get("deals", [])
        by_store = data.get("by_store", {})

        # Format deals for display
        deals_list = []
        for i, d in enumerate(deals[:20], 1):
            deals_list.append(
                f"{i}. {d.get('store', '')} | "
                f"{d.get('product', '')[:45]} | "
                f"~~{d.get('price_old', 0):.2f}~~ → {d.get('price_new', 0):.2f} lei | "
                f"-{d.get('discount_pct', 0):.0f}%"
            )

        # Format store summary
        stores_summary = []
        for store, sd in by_store.items():
            stores_summary.append(
                f"{store}: {sd.get('count', 0)} oferte, "
                f"best -{sd.get('best_discount', 0):.0f}% "
                f"({sd.get('best_product', '')[:30]})"
            )

        return {
            "deals": deals_list,
            "stores": stores_summary,
            "best_discount": data.get("best_discount", 0),
            "best_product": data.get("best_product", ""),
            "best_store": data.get("best_store", ""),
            "last_update": data.get("last_update", ""),
            # Raw data for card
            "deals_raw": deals,
            "by_store": by_store,
        }


class RetailDealsStoreSensor(RetailDealsBaseSensor):
    """Sensor for a specific store — state = count, attributes = best deal."""

    def __init__(self, coordinator, entry, store_id: str):
        super().__init__(coordinator, entry)
        self._store_id = store_id
        store_info = STORES.get(store_id, {})
        self._attr_name = f"Deals {store_info.get('name', store_id)}"
        self._attr_icon = store_info.get("icon", "mdi:store")
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
        sd = by_store.get(self._store_id, {})

        # Get deals for this store
        all_deals = data.get("deals", [])
        store_deals = [d for d in all_deals if d.get("store", "").lower() == self._store_id]

        deals_list = []
        for i, d in enumerate(store_deals[:5], 1):
            deals_list.append(
                f"{i}. {d.get('product', '')[:45]} | "
                f"~~{d.get('price_old', 0):.2f}~~ → {d.get('price_new', 0):.2f} lei | "
                f"-{d.get('discount_pct', 0):.0f}%"
            )

        return {
            "avg_discount": sd.get("avg_discount", 0),
            "best_discount": sd.get("best_discount", 0),
            "best_product": sd.get("best_product", ""),
            "deals": deals_list,
        }


class RetailDealsItemSensor(RetailDealsBaseSensor):
    """Sensor for a specific deal — state = product name!"""

    def __init__(self, coordinator, entry, index: int):
        super().__init__(coordinator, entry)
        self._index = index
        self._attr_name = f"Deal #{index + 1}"
        self._attr_icon = self._get_icon(index)
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_deal_{index}"

    @staticmethod
    def _get_icon(index: int) -> str:
        if index == 0:
            return "mdi:trophy"
        if index == 1:
            return "mdi:medal"
        if index == 2:
            return "mdi:medal-outline"
        return "mdi:tag-outline"

    @property
    def native_value(self) -> str:
        """State = product name (so it shows in HA UI)."""
        data = self.coordinator.data or {}
        deals = data.get("deals", [])
        if self._index < len(deals):
            product = deals[self._index].get("product", "")
            return product[:50] if product else "N/A"
        return "N/A"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """All deal details as attributes."""
        data = self.coordinator.data or {}
        deals = data.get("deals", [])
        if self._index < len(deals):
            d = deals[self._index]
            return {
                "store": d.get("store", ""),
                "price_old": d.get("price_old", 0),
                "price_new": d.get("price_new", 0),
                "discount_pct": d.get("discount_pct", 0),
                "savings": d.get("savings", 0),
                "url": d.get("url", ""),
                "category": d.get("category", ""),
                "brand": d.get("brand", ""),
            }
        return {}
