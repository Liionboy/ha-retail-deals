# 🛒 Retail Deals Romania — Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![GitHub release](https://img.shields.io/github/v/release/Liionboy/ha-retail-deals)](https://github.com/Liionboy/ha-retail-deals/releases)

Colectează cele mai bune reduceri de la magazinele din România direct în Home Assistant.

## 🏪 Magazine suportate

| Magazin | Sursă date | Metodă | Status |
|---------|-----------|--------|--------|
| **Auchan** | VTEX API | Direct (API) | ✅ |
| **Kaufland** | PromoAzi.ro | Playwright scraping | ✅ |
| **Lidl** | PromoAzi.ro | Playwright scraping | ✅ |
| **Carrefour** | PromoAzi.ro | Playwright scraping | ✅ |

## 📦 Instalare

### HACS (recomandat)

1. Deschide **HACS** → **Integrations** → ⋮ → **Custom repositories**
2. Adaugă URL-ul: `https://github.com/Liionboy/ha-retail-deals`
3. Selectează categoria: **Integration**
4. Click **Add**
5. Caută **"Retail Deals Romania"** și instalează
6. **Restart** Home Assistant
7. **Settings** → **Devices & Services** → **+ Add Integration** → **"Retail Deals Romania"**

### Cardul Lovelace (opțional)

Pentru cardul custom `retail-deals-card`:

1. Copiază fișierele din `www/` în directorul `www/` al HA:
   ```bash
   # Pe serverul HA
   cp www/retail-deals-card.js /config/www/
   cp www/retail-deals-card-editor.js /config/www/
   ```
2. Adaugă resursa în Lovelace:
   - **Settings** → **Dashboards** → ⋮ → **Resources** → **+ Add Resource**
   - URL: `/local/retail-deals-card.js`
   - Type: **JavaScript Module**
3. Acum poți adăuga cardul în orice dashboard: **+ Add Card** → **"Retail Deals Card"**

### Manual (fără HACS)

1. Copiază `custom_components/retail_deals/` în `config/custom_components/`
2. Restart Home Assistant
3. Adaugă integrarea din UI

## ⚙️ Configurare

Integrarea se configurează complet din UI (config_flow):

| Setare | Descriere | Default |
|--------|-----------|---------|
| **Magazine** | Ce magazine să monitorizezi | Toate 4 |
| **Top oferte** | Câte oferte să afișezi (5-50) | 20 |
| **Discount minim** | Pragul minim de reducere (5-80%) | 15% |
| **Interval actualizare** | Frecvența colectării (60-1440 min) | 360 min (6h) |

## 📊 Entități create

### Senzori principali
| Entitate | Descriere | Unitate |
|----------|-----------|---------|
| `sensor.retail_deals_summary` | Numărul total de oferte | oferte |
| `sensor.retail_deals_best` | Cel mai mare discount | % |

### Senzori pe magazin
| Entitate | Descriere |
|----------|-----------|
| `sensor.deals_auchan` | Oferte Auchan |
| `sensor.deals_kaufland` | Oferte Kaufland |
| `sensor.deals_lidl` | Oferte Lidl |
| `sensor.deals_carrefour` | Oferte Carrefour |

### Senzori individuali (top 10)
| Entitate | Descriere |
|----------|-----------|
| `sensor.retail_deal_1` | 🥇 Cel mai bun deal |
| `sensor.retail_deal_2` | 🥈 Al doilea deal |
| `sensor.retail_deal_3` | 🥉 Al treilea deal |
| ... | ... |
| `sensor.retail_deal_10` | Deal #10 |

### Atribute senzori

Fiecare senzor de deal individual conține:

```yaml
product: "Pachet bere spaniola Spanish BeerBox"
store: "Auchan"
price_old: 225.49
price_new: 139.99
savings: 85.50
discount_pct: 38.0
url: "https://www.auchan.ro/..."
```

Sensorul `summary` conține și:

```yaml
total_deals: 150
best_discount: 68
best_product: "Aripi de pui Puiul Fericit"
best_store: "Auchan"
by_store:
  auchan:
    count: 80
    avg_discount: 32.5
    best_discount: 68
    best_product: "Aripi de pui..."
  kaufland:
    count: 40
    avg_discount: 28.3
    ...
last_update: "2026-06-27T12:30:00"
deals:
  - product: "..."
    store: "..."
    price_old: 119.00
    price_new: 49.99
    discount_pct: 58
    savings: 69.01
    url: "..."
  # ... top N deals
```

## 🎨 Card Lovelace Custom

Integrarea include un card personalizat pentru dashboard:

```yaml
type: custom:retail-deals-card
entity: sensor.retail_deals_summary
title: "🛒 Cele mai bune reduceri"
show_stores: true       # Afișează badge-uri pe magazine
show_prices: true       # Afișează prețurile
show_savings: true      # Afișează economia
max_items: 10           # Numărul de oferte afișate
compact: false          # Mod compact (fără economie)
```

**Caracteristici card:**
- 🎨 Design modern cu gradient header
- 🥇🥈🥉 Medalii pentru top 3 reduceri
- 🏪 Badge-uri colorate per magazin
- 💰 Preț tăiat + preț nou + discount badge
- 📱 Responsive, funcționează pe mobile
- ⚙️ Editor pentru configurare din UI

Vezi [`examples/dashboard.yaml`](examples/dashboard.yaml) pentru mai multe exemple.

## 🔄 Servicii

| Serviciu | Descriere |
|----------|-----------|
| `retail_deals.refresh` | Forțează actualizarea datelor |

```yaml
service: retail_deals.refresh
data:
  stores:
    - auchan
    - kaufland
```

## 🤖 Automatizări exemple

### Notificare la deal > 50%
```yaml
automation:
  - alias: "Retail Deal Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.retail_deals_best
        above: 50
    action:
      - service: notify.mobile_app
        data:
          title: "🔥 Reducere mare!"
          message: >-
            {{ state_attr('sensor.retail_deals_best', 'product') }} 
            la {{ state_attr('sensor.retail_deals_best', 'store') }} 
            cu {{ states('sensor.retail_deals_best') }}% reducere!
            Preț: {{ state_attr('sensor.retail_deals_best', 'price_new') }} lei
```

### Rezumat zilnic Telegram
```yaml
automation:
  - alias: "Rezumat Reduceri Zilnic"
    trigger:
      - platform: time
        at: "09:00:00"
    action:
      - service: notify.telegram
        data:
          title: "🛒 Reduceri azi"
          message: >-
            📊 {{ states('sensor.retail_deals_summary') }} oferte
            
            {% set by_store = state_attr('sensor.retail_deals_summary', 'by_store') %}
            {% for store, data in by_store.items() %}
            • {{ store }}: {{ data.count }} oferte (Ø {{ data.avg_discount }}%)
            {% endfor %}
```

Mai multe exemple în [`examples/dashboard.yaml`](examples/dashboard.yaml).

## 📋 Cerințe

- Home Assistant **2024.1+**
- Acces internet
- **Playwright** (opțional, pentru Kaufland/Lidl/Carrefour):
  ```bash
  pip install playwright
  python3 -m playwright install chromium
  ```

## ⚠️ Limitări

- **Auchan** — API direct, date complete cu prețuri exacte
- **Kaufland/Lidl/Carrefour** — date via PromoAzi.ro (cataloage săptămânale, nu toate produsele)
- **La Cocos** — nu are sursă de date online structurată
- Playwright necesită un browser headless pe serverul HA

## 🛠️ Dezvoltare

```bash
# Clone
git clone https://github.com/Liionboy/ha-retail-deals.git
cd ha-retail-deals

# Test collector standalone
python3 -c "
from custom_components.retail_deals.collector import collect_all_deals
data = collect_all_deals(['auchan'], top=5, min_discount=20)
print(data)
"
```

## 📝 Changelog

### v1.0.0 (2026-06-27)
- 🎉 Prima versiune
- ✅ Auchan VTEX API integration
- ✅ Kaufland, Lidl, Carrefour via PromoAzi.ro
- ✅ Config flow din UI
- ✅ 14 senzori HA
- ✅ Custom Lovelace card cu editor
- ✅ Service pentru refresh manual

## 🤝 Contribuții

Contribuțiile sunt binevenite! Deschide un issue sau un PR.

## 📄 Licență

MIT License

---

**Creat cu ❤️ de Jarvis 🤖 pentru Adrian**
