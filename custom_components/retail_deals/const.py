"""Constants for the Retail Deals Romania integration."""

DOMAIN = "retail_deals"
PLATFORMS = ["sensor"]

# Config
CONF_STORES = "stores"
CONF_TOP = "top"
CONF_MIN_DISCOUNT = "min_discount"
CONF_SCAN_INTERVAL = "scan_interval"

# Defaults
DEFAULT_STORES = ["auchan", "kaufland", "lidl", "carrefour"]
DEFAULT_TOP = 20
DEFAULT_MIN_DISCOUNT = 15
DEFAULT_SCAN_INTERVAL = 360  # minutes (6 ore)

# Store info
STORES = {
    "auchan": {"name": "Auchan", "icon": "mdi:store", "color": "#e31e24"},
    "kaufland": {"name": "Kaufland", "icon": "mdi:store", "color": "#e30613"},
    "lidl": {"name": "Lidl", "icon": "mdi:store", "color": "#0050aa"},
    "carrefour": {"name": "Carrefour", "icon": "mdi:store", "color": "#004a9b"},
    "la_cocos": {"name": "La Cocos", "icon": "mdi:store", "color": "#ff6600"},
}

# Attributes
ATTR_STORE = "store"
ATTR_PRODUCT = "product"
ATTR_PRICE_OLD = "price_old"
ATTR_PRICE_NEW = "price_new"
ATTR_DISCOUNT = "discount_pct"
ATTR_SAVINGS = "savings"
ATTR_URL = "url"
ATTR_CATEGORY = "category"
ATTR_VALID_UNTIL = "valid_until"
