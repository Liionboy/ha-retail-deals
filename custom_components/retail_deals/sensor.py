"""Sensor platform for Retail Deals Romania — clean, simple, fast."""
import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, STORES, CONF_STORES, CONF_TOP, DEFAULT_STORES, DEFAULT_TOP

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    stores = entry.data.get(CONF_STORES, DEFAULT_STORES)
    top = min(int(entry.data.get(CONF_TOP, DEFAULT_TOP)), 10)

    entities = [RetailDealsSummarySensor(coordinator, entry)]
    for store_id in stores:
        entities.append(RetailDealsStoreSensor(coordinator, entry, store_id))
    for i in range(top):
        entities.append(RetailDealsItemSensor(coordinator, entry, i))

    async_add_entities(entities)


class RetailDealsBaseSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry

    @property
    def device_info(self) -> dict:
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": "Retail Deals Romania",
            "manufacturer": "Jarvis",
        }


class RetailDealsSummarySensor(RetailDealsBaseSensor):
    """Summary — state = total deals, attributes = top 10 deals with all info."""

    _attr_name = "Retail Deals"
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

        attrs = {
            "last_update": data.get("last_update", ""),
            "best_discount": f"{data.get('best_discount', 0)}%",
            "best_product": data.get("best_product", ""),
            "best_store": data.get("best_store", ""),
        }

        # Add each deal as a separate attribute — this shows in HA UI!
        for i, d in enumerate(deals[:10], 1):
            product = (d.get("product") or "")[:50]
            store = d.get("store", "")
            po = d.get("price_old", 0)
            pn = d.get("price_new", 0)
            disc = d.get("discount_pct", 0)
            savings = d.get("savings", 0)
            attrs[f"#{i} {product}"] = (
                f"{store} | {po:.2f} → {pn:.2f} lei | "
                f"-{disc:.0f}% | economie {savings:.2f} lei"
            )

        # Store summary
        for store, sd in by_store.items():
            attrs[f"magazin_{store.lower()}"] = (
                f"{sd.get('count', 0)} oferte | "
                f"Ø {sd.get('avg_discount', 0)}% | "
                f"best: {sd.get('best_product', '')[:30]}"
            )

        return attrs


class RetailDealsStoreSensor(RetailDealsBaseSensor):
    """Per-store sensor — state = count, attributes = top 5 deals."""

    def __init__(self, coordinator, entry, store_id: str):
        super().__init__(coordinator, entry)
        self._store_id = store_id
        info = STORES.get(store_id, {})
        self._attr_name = f"Deals {info.get('name', store_id)}"
        self._attr_icon = info.get("icon", "mdi:store")
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_{store_id}"

    @property
    def native_value(self) -> int:
        data = self.coordinator.data or {}
        return data.get("by_store", {}).get(self._store_id, {}).get("count", 0)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data or {}
        sd = data.get("by_store", {}).get(self._store_id, {})
        all_deals = data.get("deals", [])
        store_deals = [d for d in all_deals if d.get("store", "").lower() == self._store_id]

        attrs = {
            "avg_discount": f"{sd.get('avg_discount', 0)}%",
            "best_discount": f"{sd.get('best_discount', 0)}%",
            "best_product": sd.get("best_product", ""),
        }

        for i, d in enumerate(store_deals[:5], 1):
            product = (d.get("product") or "")[:50]
            po = d.get("price_old", 0)
            pn = d.get("price_new", 0)
            disc = d.get("discount_pct", 0)
            attrs[f"#{i} {product}"] = f"{po:.2f} → {pn:.2f} lei | -{disc:.0f}%"

        return attrs


class RetailDealsItemSensor(RetailDealsBaseSensor):
    """Individual deal sensor — state = product name, attributes = all details."""

    def __init__(self, coordinator, entry, index: int):
        super().__init__(coordinator, entry)
        self._index = index
        icons = {0: "mdi:trophy", 1: "mdi:medal", 2: "mdi:medal-outline"}
        self._attr_icon = icons.get(index, "mdi:tag-outline")
        self._attr_name = f"Deal #{index + 1}"
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_deal_{index}"

    @property
    def native_value(self) -> str:
        """Product name as state — visible in HA UI."""
        data = self.coordinator.data or {}
        deals = data.get("deals", [])
        if self._index < len(deals):
            return (deals[self._index].get("product") or "N/A")[:50]
        return "N/A"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """All deal details as simple attributes."""
        data = self.coordinator.data or {}
        deals = data.get("deals", [])
        if self._index < len(deals):
            d = deals[self._index]
            return {
                "magazin": d.get("store", ""),
                "pret_vechi": f"{d.get('price_old', 0):.2f} lei",
                "pret_nou": f"{d.get('price_new', 0):.2f} lei",
                "reducere": f"{d.get('discount_pct', 0):.0f}%",
                "economie": f"{d.get('savings', 0):.2f} lei",
                "categorie": d.get("category", ""),
                "brand": d.get("brand", ""),
                "link": d.get("url", ""),
            }
        return {}
