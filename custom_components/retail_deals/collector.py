"""Retail deals collector — optimized for speed."""
import logging
import re
from datetime import datetime
from urllib.parse import quote

import requests

_LOGGER = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/html, */*",
    "Accept-Language": "ro-RO,ro;q=0.9,en;q=0.8",
}

SESSION = requests.Session()
SESSION.headers.update(HEADERS)
SESSION.timeout = 10


def _calc_discount(old: float, new: float) -> float:
    if old <= 0 or new >= old:
        return 0.0
    return round((1 - new / old) * 100, 1)


def _safe_float(val) -> float:
    try:
        if isinstance(val, str):
            val = val.replace(",", ".").replace(" lei", "").replace("RON", "").strip()
        return float(val) if val else 0
    except (ValueError, TypeError):
        return 0.0


# ---------------------------------------------------------------------------
# Auchan — VTEX API (fast, direct)
# ---------------------------------------------------------------------------
def _collect_auchan(limit: int = 200) -> list[dict]:
    """Fetch deals from Auchan VTEX API — top categories only for speed."""
    base = "https://www.auchan.ro/api/io/_v/api/intelligent-search/product_search"
    # Top 8 categories only — fast enough
    categories = ["bere", "vin", "lapte", "carne", "pui", "cafea", "ciocolata", "detergent"]
    deals = []
    seen = set()

    for q in categories:
        try:
            url = f"{base}?query={quote(q)}&page=1&count=50"
            resp = SESSION.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            for p in data.get("products", []):
                try:
                    pr = p.get("priceRange") or {}
                    sp = pr.get("sellingPrice") or {}
                    lp = pr.get("listPrice") or {}
                    sell = _safe_float(sp.get("lowPrice"))
                    lst = _safe_float(lp.get("lowPrice"))
                except (TypeError, ValueError):
                    continue

                if lst <= 0 or sell <= 0 or sell >= lst:
                    continue

                disc = _calc_discount(lst, sell)
                if disc < 5:
                    continue

                name = p.get("productName", "")
                key = f"{name.lower()}_{sell}_{lst}"
                if key in seen:
                    continue
                seen.add(key)

                cats = p.get("categories", [])
                cat = cats[0].strip("/").split("/")[0] if cats else ""

                deals.append({
                    "store": "Auchan",
                    "product": name,
                    "price_old": lst,
                    "price_new": sell,
                    "discount_pct": disc,
                    "savings": round(lst - sell, 2),
                    "category": cat,
                    "brand": p.get("brand", ""),
                    "url": f"https://www.auchan.ro{p.get('link', '')}",
                })

        except Exception as e:
            _LOGGER.warning("Auchan [%s]: %s", q, e)

    _LOGGER.info("Auchan: %d deals", len(deals))
    return deals


# ---------------------------------------------------------------------------
# PromoAzi — Kaufland, Lidl, Carrefour (requests + BeautifulSoup)
# ---------------------------------------------------------------------------
def _collect_promoazi(store_name: str, url: str, limit: int = 100) -> list[dict]:
    """Scrape deals from promoazi.ro using requests + BeautifulSoup."""
    deals = []
    try:
        try:
            from bs4 import BeautifulSoup
            resp = SESSION.get(url, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            text = soup.get_text("\n")
        except ImportError:
            _LOGGER.warning("%s: beautifulsoup4 not installed", store_name)
            resp = SESSION.get(url, timeout=10)
            resp.raise_for_status()
            text = resp.text

        lines = [l.strip() for l in text.split("\n") if l.strip()]
        price_re = re.compile(r'(\d+[.,]\d{2})\s*lei')
        disc_re = re.compile(r'-(\d+)%')
        seen = set()

        i = 0
        while i < len(lines) and len(deals) < limit:
            line = lines[i]
            disc_match = disc_re.match(line)
            if disc_match and i + 4 < len(lines):
                name = lines[i + 1]
                price_lines = []
                for j in range(i + 2, min(i + 6, len(lines))):
                    prices = price_re.findall(lines[j])
                    if prices:
                        price_lines.extend([_safe_float(pr) for pr in prices])

                if len(price_lines) >= 2:
                    pn = min(price_lines[0], price_lines[1])
                    po = max(price_lines[0], price_lines[1])

                    if po > 0 and pn > 0 and pn < po:
                        disc = _calc_discount(po, pn)
                        key = f"{name.lower()}_{pn}_{po}"
                        if disc >= 5 and len(name) > 2 and key not in seen:
                            seen.add(key)
                            deals.append({
                                "store": store_name,
                                "product": name,
                                "price_old": po,
                                "price_new": pn,
                                "discount_pct": disc,
                                "savings": round(po - pn, 2),
                                "url": url,
                            })
            i += 1

    except Exception as e:
        _LOGGER.warning("%s: %s", store_name, e)

    _LOGGER.info("%s: %d deals", store_name, len(deals))
    return deals


# ---------------------------------------------------------------------------
# Main collector
# ---------------------------------------------------------------------------
def collect_all_deals(
    stores: list[str], top: int = 20, min_discount: float = 15
) -> dict:
    """Collect deals from all configured stores."""
    top = int(top)
    min_discount = float(min_discount)
    all_deals = []

    store_funcs = {
        "auchan": lambda: _collect_auchan(),
        "kaufland": lambda: _collect_promoazi("Kaufland", "https://promoazi.ro/cataloage/kaufland"),
        "lidl": lambda: _collect_promoazi("Lidl", "https://promoazi.ro/cataloage/lidl"),
        "carrefour": lambda: _collect_promoazi("Carrefour", "https://promoazi.ro/cataloage/carrefour"),
    }

    for store in stores:
        func = store_funcs.get(store)
        if func:
            try:
                deals = func()
                all_deals.extend(deals)
            except Exception as e:
                _LOGGER.error("Error collecting %s: %s", store, e)

    # Filter
    all_deals = [d for d in all_deals if d["discount_pct"] >= min_discount]

    # Deduplicate
    seen = set()
    unique = []
    for d in all_deals:
        key = (d["store"], d.get("product", "").lower().strip())
        if key not in seen:
            seen.add(key)
            unique.append(d)

    # Sort by discount
    unique.sort(key=lambda d: d["discount_pct"], reverse=True)
    top_deals = unique[:top]

    # Stats by store
    by_store = {}
    for d in unique:
        by_store.setdefault(d["store"], []).append(d)

    stats = {}
    for store, sd in by_store.items():
        best = max(sd, key=lambda x: x["discount_pct"])
        stats[store] = {
            "count": len(sd),
            "avg_discount": round(sum(d["discount_pct"] for d in sd) / len(sd), 1),
            "best_discount": best["discount_pct"],
            "best_product": (best.get("product") or "")[:60],
        }

    return {
        "deals": top_deals,
        "total_deals": len(unique),
        "top_deals": len(top_deals),
        "by_store": stats,
        "last_update": datetime.now().isoformat(),
        "best_discount": top_deals[0]["discount_pct"] if top_deals else 0,
        "best_product": (top_deals[0].get("product") or "") if top_deals else "",
        "best_store": top_deals[0].get("store", "") if top_deals else "",
    }
