/**
 * 🛒 Retail Deals Card — Custom Lovelace card for Retail Deals Romania
 * 
 * Afișează cele mai bune reduceri de la magazinele din România
 * într-un card modern și atractiv.
 * 
 * Utilizare în dashboard:
 * type: custom:retail-deals-card
 * entity: sensor.retail_deals_summary
 * title: "🛒 Cele mai bune reduceri"
 * show_stores: true
 * max_items: 10
 */

class RetailDealsCard extends HTMLElement {
  static getConfigElement() {
    return document.createElement("retail-deals-card-editor");
  }

  static getStubConfig() {
    return {
      entity: "sensor.retail_deals_summary",
      title: "🛒 Cele mai bune reduceri",
      show_stores: true,
      max_items: 10,
      show_prices: true,
      show_savings: true,
      compact: false,
    };
  }

  setConfig(config) {
    if (!config.entity) {
      throw new Error("Entity is required!");
    }
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
          <div class="card-content">
            <div class="not-found">
              <ha-icon icon="mdi:alert-circle"></ha-icon>
              <span>Entity ${this._config.entity} not found</span>
            </div>
          </div>
        </ha-card>
      `;
      return;
    }

    const attrs = entity.attributes || {};
    const deals = attrs.deals || [];
    const byStore = attrs.by_store || {};
    const maxItems = this._config.max_items || 10;
    const showStores = this._config.show_stores !== false;
    const showPrices = this._config.show_prices !== false;
    const showSavings = this._config.show_savings !== false;
    const compact = this._config.compact || false;

    const storeColors = {
      auchan: "#e31e24",
      kaufland: "#e30613",
      lidl: "#0050aa",
      carrefour: "#004a9b",
      la_cocos: "#ff6600",
    };

    const storeIcons = {
      auchan: "mdi:store",
      kaufland: "mdi:store",
      lidl: "mdi:store",
      carrefour: "mdi:store",
      la_cocos: "mdi:store",
    };

    // Build deals HTML
    let dealsHtml = "";
    const displayDeals = deals.slice(0, maxItems);

    displayDeals.forEach((deal, index) => {
      const storeColor =
        storeColors[deal.store?.toLowerCase()] || "#666";
      const storeIcon =
        storeIcons[deal.store?.toLowerCase()] || "mdi:store";
      const discount = deal.discount_pct || 0;
      const discountClass =
        discount >= 40 ? "discount-hot" : discount >= 25 ? "discount-warm" : "discount-cool";

      const medal =
        index === 0 ? "🥇" : index === 1 ? "🥈" : index === 2 ? "🥉" : `#${index + 1}`;

      dealsHtml += `
        <div class="deal-item ${compact ? "compact" : ""}">
          <div class="deal-rank">${medal}</div>
          <div class="deal-info">
            <div class="deal-name">${deal.product || "N/A"}</div>
            <div class="deal-store" style="color: ${storeColor}">
              <ha-icon icon="${storeIcon}" style="--mdc-icon-size: 14px;"></ha-icon>
              ${deal.store || ""}
            </div>
          </div>
          ${showPrices ? `
          <div class="deal-prices">
            <span class="price-old">${deal.price_old?.toFixed(2) || ""} lei</span>
            <span class="price-new">${deal.price_new?.toFixed(2) || ""} lei</span>
          </div>
          ` : ""}
          <div class="deal-discount ${discountClass}">
            -${discount}%
          </div>
          ${showSavings ? `
          <div class="deal-savings">
            Economisești ${deal.savings?.toFixed(2) || ""} lei
          </div>
          ` : ""}
        </div>
      `;
    });

    // Build stores summary
    let storesHtml = "";
    if (showStores && Object.keys(byStore).length > 0) {
      storesHtml = '<div class="stores-summary">';
      Object.entries(byStore).forEach(([store, data]) => {
        const color = storeColors[store.toLowerCase()] || "#666";
        storesHtml += `
          <div class="store-badge" style="border-color: ${color}">
            <span class="store-name">${store}</span>
            <span class="store-count">${data.count || 0} oferte</span>
            <span class="store-avg">Ø ${data.avg_discount || 0}%</span>
          </div>
        `;
      });
      storesHtml += "</div>";
    }

    // Last update
    const lastUpdate = attrs.last_update
      ? new Date(attrs.last_update).toLocaleString("ro-RO")
      : "Necunoscut";

    this.innerHTML = `
      <ha-card>
        <div class="card-header">
          <div class="header-title">
            <ha-icon icon="mdi:shopping"></ha-icon>
            <span>${this._config.title || "🛒 Retail Deals"}</span>
          </div>
          <div class="header-stats">
            <span class="stat-badge">
              <ha-icon icon="mdi:tag-multiple" style="--mdc-icon-size: 16px;"></ha-icon>
              ${entity.state || 0} oferte
            </span>
            <span class="stat-badge hot">
              <ha-icon icon="mdi:fire" style="--mdc-icon-size: 16px;"></ha-icon>
              -${attrs.best_discount || 0}%
            </span>
          </div>
        </div>
        
        ${storesHtml}
        
        <div class="deals-list">
          ${dealsHtml || '<div class="no-deals">Nu sunt reduceri disponibile</div>'}
        </div>
        
        <div class="card-footer">
          <span class="last-update">
            <ha-icon icon="mdi:clock-outline" style="--mdc-icon-size: 14px;"></ha-icon>
            Actualizat: ${lastUpdate}
          </span>
          ${attrs.best_product ? `
          <span class="best-deal">
            <ha-icon icon="mdi:star" style="--mdc-icon-size: 14px;"></ha-icon>
            Best: ${attrs.best_product?.substring(0, 30)}...
          </span>
          ` : ""}
        </div>
      </ha-card>
      
      <style>
        ha-card {
          overflow: hidden;
          border-radius: 12px;
        }
        
        .card-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 16px;
          background: linear-gradient(135deg, var(--primary-color) 0%, var(--accent-color) 100%);
          color: white;
        }
        
        .header-title {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 1.1em;
          font-weight: 600;
        }
        
        .header-stats {
          display: flex;
          gap: 8px;
        }
        
        .stat-badge {
          display: flex;
          align-items: center;
          gap: 4px;
          padding: 4px 10px;
          background: rgba(255,255,255,0.2);
          border-radius: 20px;
          font-size: 0.85em;
          font-weight: 500;
        }
        
        .stat-badge.hot {
          background: rgba(255,87,34,0.8);
        }
        
        .stores-summary {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
          padding: 12px 16px;
          background: var(--card-background-color, #fff);
          border-bottom: 1px solid var(--divider-color, #e0e0e0);
        }
        
        .store-badge {
          display: flex;
          flex-direction: column;
          align-items: center;
          padding: 8px 12px;
          border: 2px solid;
          border-radius: 8px;
          min-width: 80px;
        }
        
        .store-name {
          font-weight: 600;
          font-size: 0.9em;
        }
        
        .store-count {
          font-size: 0.75em;
          opacity: 0.7;
        }
        
        .store-avg {
          font-size: 0.75em;
          color: var(--error-color, #f44336);
          font-weight: 500;
        }
        
        .deals-list {
          padding: 8px 0;
        }
        
        .deal-item {
          display: grid;
          grid-template-columns: 40px 1fr auto auto;
          grid-template-rows: auto auto;
          gap: 4px 12px;
          padding: 12px 16px;
          border-bottom: 1px solid var(--divider-color, #e0e0e0);
          align-items: center;
          transition: background 0.2s;
        }
        
        .deal-item:hover {
          background: var(--secondary-background-color, #f5f5f5);
        }
        
        .deal-item.compact {
          padding: 8px 16px;
          grid-template-rows: auto;
        }
        
        .deal-rank {
          font-size: 1.2em;
          text-align: center;
          grid-row: 1 / 3;
        }
        
        .deal-item.compact .deal-rank {
          grid-row: 1;
        }
        
        .deal-info {
          min-width: 0;
        }
        
        .deal-name {
          font-weight: 500;
          font-size: 0.95em;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }
        
        .deal-store {
          display: flex;
          align-items: center;
          gap: 4px;
          font-size: 0.8em;
          opacity: 0.8;
        }
        
        .deal-prices {
          display: flex;
          flex-direction: column;
          align-items: flex-end;
          gap: 2px;
        }
        
        .price-old {
          text-decoration: line-through;
          opacity: 0.5;
          font-size: 0.8em;
        }
        
        .price-new {
          font-weight: 700;
          font-size: 1em;
          color: var(--success-color, #4caf50);
        }
        
        .deal-discount {
          padding: 4px 10px;
          border-radius: 20px;
          font-weight: 700;
          font-size: 0.9em;
          text-align: center;
          min-width: 50px;
        }
        
        .discount-hot {
          background: #ffebee;
          color: #c62828;
        }
        
        .discount-warm {
          background: #fff3e0;
          color: #e65100;
        }
        
        .discount-cool {
          background: #e3f2fd;
          color: #1565c0;
        }
        
        .deal-savings {
          grid-column: 2 / 5;
          font-size: 0.75em;
          color: var(--success-color, #4caf50);
          font-weight: 500;
        }
        
        .deal-item.compact .deal-savings {
          grid-column: auto;
          display: none;
        }
        
        .no-deals {
          padding: 24px;
          text-align: center;
          opacity: 0.5;
        }
        
        .card-footer {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 12px 16px;
          font-size: 0.75em;
          opacity: 0.6;
          border-top: 1px solid var(--divider-color, #e0e0e0);
        }
        
        .last-update, .best-deal {
          display: flex;
          align-items: center;
          gap: 4px;
        }
        
        .not-found {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 16px;
          color: var(--error-color, #f44336);
        }
      </style>
    `;
  }
}

customElements.define("retail-deals-card", RetailDealsCard);

// Register in HACS
window.customCards = window.customCards || [];
window.customCards.push({
  type: "retail-deals-card",
  name: "Retail Deals Card",
  description: "🛒 Afișează cele mai bune reduceri de la magazinele din România",
  preview: true,
  documentationURL: "https://github.com/Liionboy/ha-retail-deals",
});

console.info(
  "%c 🛒 RETAIL-DEALS-CARD %c v1.0.0 ",
  "color: white; background: #e31e24; font-weight: 700;",
  "color: #e31e24; background: white; font-weight: 700;"
);
