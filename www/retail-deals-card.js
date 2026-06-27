/**
 * 🛒 Retail Deals Card v1.0.8 — reads from sensor attributes
 *
 * type: custom:retail-deals-card
 * entity: sensor.retail_deals
 * title: "🛒 Cele mai bune reduceri"
 * max_items: 10
 */

class RetailDealsCard extends HTMLElement {
  static getStubConfig() {
    return {
      entity: "sensor.retail_deals",
      title: "🛒 Cele mai bune reduceri",
      max_items: 10,
      show_stores: true,
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
      this.innerHTML = `<ha-card><div class="not-found">Entity ${this._config.entity} not found</div></ha-card>`;
      return;
    }

    const attrs = entity.attributes || {};
    const maxItems = this._config.max_items || 10;
    const showStores = this._config.show_stores !== false;

    const storeColors = {
      auchan: "#e31e24", kaufland: "#e30613",
      lidl: "#0050aa", carrefour: "#004a9b",
    };

    // Parse deals from attributes: "#1 Product Name": "Store | old → new lei | -XX%"
    const dealEntries = [];
    const storeEntries = [];

    Object.entries(attrs).forEach(([key, val]) => {
      if (key.startsWith("#")) {
        dealEntries.push({ key, val });
      } else if (key.startsWith("magazin_")) {
        storeEntries.push({ key, val });
      }
    });

    // Build deals HTML
    let dealsHtml = "";
    dealEntries.slice(0, maxItems).forEach((entry, i) => {
      const name = entry.key.replace(/^#\d+\s*/, "");
      const parts = String(entry.val).split("|").map(s => s.trim());
      const store = parts[0] || "";
      const priceInfo = parts[1] || "";
      const discInfo = parts[2] || "";
      const savingsInfo = parts[3] || "";

      // Parse prices: "119.00 → 49.99 lei"
      const priceMatch = priceInfo.match(/([\d.]+)\s*→\s*([\d.]+)\s*lei/);
      const priceOld = priceMatch ? priceMatch[1] : "";
      const priceNew = priceMatch ? priceMatch[2] : "";

      // Parse discount: "-58%"
      const discMatch = discInfo.match(/-(\d+)%/);
      const disc = discMatch ? parseInt(discMatch[1]) : 0;
      const discClass = disc >= 40 ? "hot" : disc >= 25 ? "warm" : "cool";

      // Parse savings: "economie 69.01 lei"
      const savMatch = savingsInfo.match(/([\d.]+)\s*lei/);
      const savings = savMatch ? savMatch[1] : "";

      const medal = i === 0 ? "🥇" : i === 1 ? "🥈" : i === 2 ? "🥉" : `#${i + 1}`;
      const storeLower = store.toLowerCase();
      const color = storeColors[storeLower] || "#666";

      dealsHtml += `
        <div class="deal">
          <div class="rank">${medal}</div>
          <div class="info">
            <div class="name">${name}</div>
            <div class="store" style="color:${color}">${store}</div>
          </div>
          ${priceOld ? `<div class="prices"><span class="old">${priceOld} lei</span><span class="new">${priceNew} lei</span></div>` : ""}
          ${disc ? `<div class="disc ${discClass}">-${disc}%</div>` : ""}
          ${savings ? `<div class="sav">-${savings} lei</div>` : ""}
        </div>`;
    });

    // Stores summary
    let storesHtml = "";
    if (showStores && storeEntries.length > 0) {
      storesHtml = '<div class="stores">';
      storeEntries.forEach((entry) => {
        const storeName = entry.key.replace("magazin_", "");
        const displayName = storeName.charAt(0).toUpperCase() + storeName.slice(1);
        const color = storeColors[storeName] || "#666";
        storesHtml += `<div class="sbadge" style="border-color:${color}"><span class="sn">${displayName}</span><span class="sd">${entry.val}</span></div>`;
      });
      storesHtml += "</div>";
    }

    const lastUpdate = attrs.last_update ? new Date(attrs.last_update).toLocaleString("ro-RO") : "";

    this.innerHTML = `
      <ha-card>
        <div class="header">
          <div class="htitle"><ha-icon icon="mdi:shopping"></ha-icon><span>${this._config.title}</span></div>
          <div class="hstats">
            <span class="badge"><ha-icon icon="mdi:tag-multiple" style="--mdc-icon-size:16px"></ha-icon> ${entity.state} oferte</span>
            ${attrs.best_discount ? `<span class="badge hot"><ha-icon icon="mdi:fire" style="--mdc-icon-size:16px"></ha-icon> ${attrs.best_discount}</span>` : ""}
          </div>
        </div>
        ${storesHtml}
        <div class="deals">${dealsHtml || '<div class="empty">Nu sunt reduceri disponibile</div>'}</div>
        ${lastUpdate ? `<div class="footer"><ha-icon icon="mdi:clock-outline" style="--mdc-icon-size:14px"></ha-icon> ${lastUpdate}</div>` : ""}
      </ha-card>

      <style>
        ha-card{overflow:hidden;border-radius:12px}
        .header{display:flex;justify-content:space-between;align-items:center;padding:16px;background:linear-gradient(135deg,var(--primary-color),var(--accent-color));color:#fff;flex-wrap:wrap;gap:8px}
        .htitle{display:flex;align-items:center;gap:8px;font-size:1.1em;font-weight:600}
        .hstats{display:flex;gap:8px}
        .badge{display:flex;align-items:center;gap:4px;padding:4px 10px;background:rgba(255,255,255,.2);border-radius:20px;font-size:.85em;font-weight:500}
        .badge.hot{background:rgba(255,87,34,.8)}
        .stores{display:flex;flex-wrap:wrap;gap:8px;padding:12px 16px;border-bottom:1px solid var(--divider-color,#e0e0e0)}
        .sbadge{display:flex;flex-direction:column;align-items:center;padding:8px 12px;border:2px solid;border-radius:8px;min-width:80px}
        .sn{font-weight:600;font-size:.85em;text-transform:capitalize}
        .sd{font-size:.7em;opacity:.7;max-width:100px;text-align:center;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
        .deals{padding:8px 0}
        .deal{display:grid;grid-template-columns:36px 1fr auto auto;gap:4px 10px;padding:10px 16px;border-bottom:1px solid var(--divider-color,#e0e0e0);align-items:center}
        .deal:hover{background:var(--secondary-background-color,#f5f5f5)}
        .rank{font-size:1.1em;text-align:center}
        .info{min-width:0}
        .name{font-weight:500;font-size:.9em;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:200px}
        .store{font-size:.75em;opacity:.7;font-weight:600}
        .prices{display:flex;flex-direction:column;align-items:flex-end;gap:1px}
        .old{text-decoration:line-through;opacity:.4;font-size:.75em}
        .new{font-weight:700;font-size:.9em;color:var(--success-color,#4caf50)}
        .disc{padding:3px 8px;border-radius:16px;font-weight:700;font-size:.8em;text-align:center;min-width:44px}
        .disc.hot{background:#ffebee;color:#c62828}
        .disc.warm{background:#fff3e0;color:#e65100}
        .disc.cool{background:#e3f2fd;color:#1565c0}
        .sav{font-size:.7em;color:var(--success-color,#4caf50);font-weight:500}
        .empty{padding:24px;text-align:center;opacity:.5}
        .footer{display:flex;align-items:center;gap:4px;padding:10px 16px;font-size:.7em;opacity:.5;border-top:1px solid var(--divider-color,#e0e0e0)}
        .not-found{padding:16px;color:var(--error-color,#f44336)}
      </style>`;
  }
}

customElements.define("retail-deals-card", RetailDealsCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: "retail-deals-card",
  name: "Retail Deals Card",
  description: "🛒 Cele mai bune reduceri din Romania",
  preview: true,
});

console.info("%c 🛒 RETAIL-DEALS-CARD %c v1.0.8 ", "color:#fff;background:#e31e24;font-weight:700", "color:#e31e24;background:#fff;font-weight:700");
