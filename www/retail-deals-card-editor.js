/**
 * Retail Deals Card — Editor pentru configurare din UI
 */

class RetailDealsCardEditor extends HTMLElement {
  setConfig(config) {
    this._config = config;
    this._render();
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  _render() {
    if (!this._hass || !this._config) return;

    this.innerHTML = `
      <div class="card-config">
        <ha-entity-picker
          .hass="${this._hass}"
          .value="${this._config.entity || ""}"
          .configValue="${"entity"}"
          .includeDomains="${["sensor"]}"
          .label="${"Entity"}"
          @value-changed="${this._valueChanged}"
          allow-custom-entity
        ></ha-entity-picker>
        
        <ha-textfield
          .label="${"Title"}"
          .value="${this._config.title || ""}"
          .configValue="${"title"}"
          @input="${this._valueChanged}"
        ></ha-textfield>
        
        <ha-formfield .label="${"Show stores"}">
          <ha-switch
            .checked="${this._config.show_stores !== false}"
            .configValue="${"show_stores"}"
            @change="${this._valueChanged}"
          ></ha-switch>
        </ha-formfield>
        
        <ha-formfield .label="${"Show prices"}">
          <ha-switch
            .checked="${this._config.show_prices !== false}"
            .configValue="${"show_prices"}"
            @change="${this._valueChanged}"
          ></ha-switch>
        </ha-formfield>
        
        <ha-formfield .label="${"Show savings"}">
          <ha-switch
            .checked="${this._config.show_savings !== false}"
            .configValue="${"show_savings"}"
            @change="${this._valueChanged}"
          ></ha-switch>
        </ha-formfield>
        
        <ha-formfield .label="${"Compact mode"}">
          <ha-switch
            .checked="${this._config.compact || false}"
            .configValue="${"compact"}"
            @change="${this._valueChanged}"
          ></ha-switch>
        </ha-formfield>
        
        <ha-textfield
          .label="${"Max items"}"
          .value="${this._config.max_items || 10}"
          .configValue="${"max_items"}"
          type="number"
          min="1"
          max="50"
          @input="${this._valueChanged}"
        ></ha-textfield>
      </div>
      
      <style>
        .card-config {
          display: flex;
          flex-direction: column;
          gap: 16px;
          padding: 16px;
        }
        
        ha-entity-picker,
        ha-textfield {
          width: 100%;
        }
        
        ha-formfield {
          display: flex;
          align-items: center;
        }
      </style>
    `;
  }

  _valueChanged(ev) {
    if (!this._config || !this._hass) return;

    const target = ev.target;
    const configValue = target.configValue;
    let value = target.value;

    if (target.type === "checkbox" || target.tagName === "HA-SWITCH") {
      value = target.checked;
    }

    if (target.type === "number") {
      value = parseInt(value, 10);
    }

    const newConfig = { ...this._config };
    newConfig[configValue] = value;

    const event = new CustomEvent("config-changed", {
      detail: { config: newConfig },
      bubbles: true,
      composed: true,
    });
    this.dispatchEvent(event);
  }
}

customElements.define("retail-deals-card-editor", RetailDealsCardEditor);
