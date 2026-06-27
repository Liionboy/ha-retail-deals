/**
 * 🛒 Retail Deals Card v1.0.7 — Custom Lovelace card
 * 
 * Afișează cele mai bune reduceri de la magazinele din România.
 * 
 * Usage:
 * type: custom:retail-deals-card
 * entity: sensor.retail_deals_summary
 * title: "🛒 Cele mai bune reduceri"
 * max_items: 10
 */

class RetailDealsCard extends HTMLElement {
  static getStubConfig() {
    return {
      entity: "sensor.retail_deals_summary",
      title: "🛒 Cele mai bune reduceri",
      max_items: 10,
      show_stores: true,
      compact: false,
    };
  }

  setConfig(config) {
    if (!config.entity) throw new Error("Entity required!");
    this._config = { ...RetailDealsCard.getStubConfig(), ...config };
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  getCardSize() {
    return 3;
  }

  _render() {
    if (!this._config || !this._hass) return;

    const entity = this._hass.states[this._config.entity];
    if (!entity) {
      this.innerHTML = `
        <ha-card>
          <div class="card-content not-found">
            <ha-icon icon="mdi:alert-circle"></ha-icon>
            <span>Entity ${this._config.entity} not found</span>
          </div>
        </ha-card>`;
      return;
    }

    const attrs = entity.attributes || {};
    // Read from deals_raw (structured data) or deals (formatted strings)
    const dealsRaw = attrs.deals_raw || [];
    const dealsFormatted = attrs.deals || [];
    const byStore = attrs.by_store || {};
    const maxItems = this._config.max_items || 10;
    const showStores = this._config.show_stores !== false;
    const compact = this._config.compact || false;

    const storeColors = {
      auchan: "#e31e24", kaufland: "#e30613",
      lidl: "#0050aa", carrefour: "#004a9b",
    };

    // Build deals HTML
    let dealsHtml = "";
    const displayDeals = dealsRaw.slice(0, maxItems);

    if (displayDeals.length === 0 && dealsFormatted.length > 0) {
      // Fallback: use formatted strings
      dealsFormatted.slice(0, maxItems).forEach((line, i) => {
        dealsHtml += `<div class="deal-item-fmt">${line}</div>`;
      });
    } else {
      displayDeals.forEach((deal, i) => {
        const store = deal.store || "";
        const storeLower = store.toLowerCase();
        const color = storeColors[storeLower] || "#666";
        const disc = deal.discount_pct || 0;
        const discClass = disc >= 40 ? "hot" : disc >= 25 ? "warm" : "cool";
        const medal = i === 0 ? "🥇" : i === 1 ? "🥈" : i === 2 ? "🥉" : `#${i + 1}`;

        dealsHtml += `
          <div class="deal-item ${compact ? "compact" : ""}">
            <div class="rank">${medal}</div>
            <div class="info">
              <div class="name">${deal.product || "N/A"}</div>
              <div class="store" style="color:${color}">
                <ha-icon icon="mdi:store" style="--mdc-icon-size:14px"></ha-icon>
                ${store}
              </div>
            </div>
            <div class="prices">
              <span class="old">${(deal.price_old || 0).toFixed(2)} lei</span>
              <span class="new">${(deal.price_new || 0).toFixed(2)} lei</span>
            </div>
            <div class="discount ${discClass}">-${disc}%</div>
            ${!compact ? `<div class="savings">Economie ${(deal.savings || 0).toFixed(2)} lei</div>` : ""}
            ${deal.url ? `<a class="link" href="${deal.url}" target="_blank" rel="noopener"><ha-icon icon="mdi:open-in-new" style="--mdc-icon-size:14px"></ha-icon></a>` : ""}
          </div>`;
      });
    }

    // Stores summary
    let storesHtml = "";
    if (showStores && Object.keys(byStore).length > 0) {
      storesHtml = '<div class="stores">';
      Object.entries(byStore).forEach(([store, data]) => {
        const color = storeColors[store.toLowerCase()] || "#666";
        storesHtml += `
          <div class="store-badge" style="border-color:${color}">
            <span class="sname">${store}</span>
            <span class="scnt">${data.count || 0} oferte</span>
            <span class="savg">Ø ${data.avg_discount || 0}%</span>
          </div>`;
      });
      storesHtml += "</div>";
    }

    const lastUpdate = attrs.last_update
      ? new Date(attrs.last_update).toLocaleString("ro-RO")
      : "N/A";

    this.innerHTML = `
      <ha-card>
        <div class="header">
          <div class="htitle">
            <ha-icon icon="mdi:shopping"></ha-icon>
            <span>${this._config.title || "🛒 Retail Deals"}</span>
          </div>
          <div class="hstats">
            <span class="badge"><ha-icon icon="mdi:tag-multiple" style="--mdc-icon-size:16px"></ha-icon> ${entity.state || 0} oferte</span>
            <span class="badge hot"><ha-icon icon="mdi:fire" style="--mdc-icon-size:16px"></ha-icon> -${attrs.best_discount || 0}%</span>
          </div>
        </div>
        ${storesHtml}
        <div class="deals">
          ${dealsHtml || '<div class="empty">Nu sunt reduceri disponibile</div>'}
        </div>
        <div class="footer">
          <span><ha-icon icon="mdi:clock-outline" style="--mdc-icon-size:14px"></ha-icon> ${lastUpdate}</span>
          ${attrs.best_product ? `<span><ha-icon icon="mdi:star" style="--mdc-icon-size:14px"></ha-icon> ${String(attrs.best_product).substring(0, 35)}...</span>` : ""}
        </div>
      </ha-card>

      <style>
        ha-card { overflow:hidden; border-radius:12px; }
        .header { display:flex; justify-content:space-between; align-items:center; padding:16px; background:linear-gradient(135deg,var(--primary-color),var(--accent-color)); color:#fff; flex-wrap:wrap; gap:8px; }
        .htitle { display:flex; align-items:center; gap:8px; font-size:1.1em; font-weight:600; }
        .hstats { display:flex; gap:8px; }
        .badge { display:flex; align-items:center; gap:4px; padding:4px 10px; background:rgba(255,255,255,.2); border-radius:20px; font-size:.85em; font-weight:500; }
        .badge.hot { background:rgba(255,87,34,.8); }
        .stores { display:flex; flex-wrap:wrap; gap:8px; padding:12px 16px; border-bottom:1px solid var(--divider-color,#e0e0e0); }
        .store-badge { display:flex; flex-direction:column; align-items:center; padding:8px 12px; border:2px solid; border-radius:8px; min-width:80px; }
        .sname { font-weight:600; font-size:.9em; }
        .scnt { font-size:.75em; opacity:.7; }
        .savg { font-size:.75em; color:var(--error-color,#f44336); font-weight:500; }
        .deals { padding:8px 0; }
        .deal-item { display:grid; grid-template-columns:40px 1fr auto auto auto; gap:4px 12px; padding:12px 16px; border-bottom:1px solid var(--divider-color,#e0e0e0); align-items:center; }
        .deal-item:hover { background:var(--secondary-background-color,#f5f5f5); }
        .deal-item.compact { padding:8px 16px; }
        .deal-item.compact .savings { display:none; }
        .rank { font-size:1.2em; text-align:center; }
        .info { min-width:0; }
        .name { font-weight:500; font-size:.95em; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:250px; }
        .store { display:flex; align-items:center; gap:4px; font-size:.8em; opacity:.8; }
        .prices { display:flex; flex-direction:column; align-items:flex-end; gap:2px; }
        .old { text-decoration:line-through; opacity:.5; font-size:.8em; }
        .new { font-weight:700; font-size:1em; color:var(--success-color,#4caf50); }
        .discount { padding:4px 10px; border-radius:20px; font-weight:700; font-size:.9em; text-align:center; min-width:50px; }
        .discount.hot { background:#ffebee; color:#c62828; }
        .discount.warm { background:#fff3e0; color:#e65100; }
        .discount.cool { background:#e3f2fd; color:#1565c0; }
        .savings { font-size:.75em; color:var(--success-color,#4caf50); font-weight:500; grid-column:2/5; }
        .link { text-decoration:none; opacity:.5; }
        .link:hover { opacity:1; }
        .deal-item-fmt { padding:8px 16px; border-bottom:1px solid var(--divider-color,#e0e0e0); font-size:.9em; }
        .empty { padding:24px; text-align:center; opacity:.5; }
        .footer { display:flex; justify-content:space-between; padding:12px 16px; font-size:.75em; opacity:.6; border-top:1px solid var(--divider-color,#e0e0e0); flex-wrap:wrap; gap:4px; }
        .footer span { display:flex; align-items:center; gap:4px; }
        .not-found { display:flex; align-items:center; gap:8px; padding:16px; color:var(--error-color,#f44336); }
      </style>`;
  }
}

customElements.define("retail-deals-card", RetailDealsCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: "retail-deals-card",
  name: "Retail Deals Card",
  description: "🛒 Cele mai bune reduceri din România",
  preview: true,
  documentationURL: "https://github.com/Liionboy/ha-retail-deals",
});

console.info(
  "%c 🛒 RETAIL-DEALS-CARD %c v1.0.7 ",
  "color:#fff; background:#e31e24; font-weight:700",
  "color:#e31e24; background:#fff; font-weight:700"
);
