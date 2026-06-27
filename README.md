# 🛒 Retail Deals Romania — Home Assistant Integration

Colectează cele mai bune reduceri de la magazinele din România direct în Home Assistant.

## Magazine suportate

| Magazin | Sursă date | Status |
|---------|-----------|--------|
| **Auchan** | VTEX API (direct) | ✅ |
| **Kaufland** | PromoAzi.ro | ✅ |
| **Lidl** | PromoAzi.ro | ✅ |
| **Carrefour** | PromoAzi.ro | ✅ |

## Instalare

### HACS (recomandat)
1. Adaugă repository-ul ca integrare custom în HACS
2. Caută "Retail Deals Romania"
3. Instalează
4. Restart Home Assistant
5. Settings → Devices & Services → Add Integration → Retail Deals Romania

### Manual
1. Copiază `custom_components/retail_deals/` în `config/custom_components/`
2. Restart Home Assistant
3. Adaugă integrarea din UI

## Configurare

Integrarea se configurează din UI (config_flow):

- **Magazine** — selectezi ce magazine să monitorizezi
- **Top oferte** — câte oferte să afișezi (5-50)
- **Discount minim** — pragul minim de reducere (5-80%)
- **Interval actualizare** — cât de des să colecteze date (60-1440 minute)

## Entități create

### Senzori principali
- `sensor.retail_deals_summary` — numărul total de oferte
- `sensor.retail_deals_best` — cel mai mare discount (%)

### Senzori pe magazin
- `sensor.deals_auchan` — oferte Auchan
- `sensor.deals_kaufland` — oferte Kaufland
- `sensor.deals_lidl` — oferte Lidl
- `sensor.deals_carrefour` — oferte Carrefour

### Senzori individuali (top 10)
- `sensor.retail_deal_1` — cel mai bun deal
- `sensor.retail_deal_2` — al doilea deal
- ... etc.

## Atribute senzori

Fiecare senzor de deal are:
- `product` — numele produsului
- `store` — magazinul
- `price_old` — prețul vechi
- `price_new` — prețul nou
- `savings` — economia (lei)
- `url` — link către ofertă

## Automatizări exemple

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
          message: >
            {{ state_attr('sensor.retail_deals_best', 'product') }} 
            la {{ state_attr('sensor.retail_deals_best', 'store') }} 
            cu {{ states('sensor.retail_deals_best') }}% reducere!
            Preț: {{ state_attr('sensor.retail_deals_best', 'price_new') }} lei
```

### Dashboard card
```yaml
type: entities
title: 🛒 Cele mai bune reduceri
entities:
  - entity: sensor.retail_deals_summary
    name: Total oferte
  - entity: sensor.retail_deals_best
    name: Cel mai bun discount
  - entity: sensor.retail_deal_1
    name: "🥇 Deal #1"
  - entity: sensor.retail_deal_2
    name: "🥈 Deal #2"
  - entity: sensor.retail_deal_3
    name: "🥉 Deal #3"
```

## Cerințe

- Home Assistant 2024.1+
- Acces internet (pentru colectarea datelor)
- Playwright (opțional, pentru Kaufland/Lidl/Carrefour)

## Limitări

- **Auchan** — API direct, date complete
- **Kaufland/Lidl/Carrefour** — date via PromoAzi.ro (cataloage săptămânale, nu toate produsele)
- **La Cocos** — nu are sursă de date online

## Suport

Issues: deschide un issue pe GitHub
