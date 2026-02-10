import { LitElement, html, css, nothing } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';
import { themeStyles } from '../styles/theme';
import { animationStyles } from '../styles/animations';
import { cardStyles } from '../styles/card-styles';
import type { HomeAssistant, HassEntity } from '../utils/ha-api';
import { getEntityState, callService, getRoomName } from '../utils/ha-api';
import {
  formatTemp,
  formatScore,
  getComfortColor,
  getComfortLabel,
  getTrendArrow,
  getHvacIcon,
  getHvacColor,
  formatDuration,
} from '../utils/formatters';

/**
 * <room-detail> component
 * Full-page drawer/modal overlay showing detailed room information and controls.
 */
@customElement('room-detail')
export class RoomDetail extends LitElement {
  @property({ attribute: false }) hass!: HomeAssistant;
  @property({ type: String }) roomSlug: string = '';
  @property({ type: Boolean }) open: boolean = false;

  @state() private _targetTemp: number = 72;
  @state() private _hvacMode: string = 'auto';

  static styles = [
    themeStyles,
    animationStyles,
    cardStyles,
    css`
      :host {
        display: block;
      }

      /* Overlay backdrop */
      .detail-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.7);
        backdrop-filter: blur(6px);
        -webkit-backdrop-filter: blur(6px);
        z-index: 1000;
        display: flex;
        align-items: flex-end;
        justify-content: center;
      }

      /* Drawer panel */
      .detail-drawer {
        width: 100%;
        max-width: 500px;
        max-height: 90vh;
        background: var(--sc-card-bg-solid);
        border-radius: var(--sc-radius-xl) var(--sc-radius-xl) 0 0;
        overflow-y: auto;
        padding: var(--sc-space-lg);
        animation: sc-slide-up 0.35s cubic-bezier(0.4, 0, 0.2, 1) forwards;
      }

      /* Close handle */
      .detail-handle {
        width: 40px;
        height: 4px;
        background: var(--sc-text-muted);
        border-radius: 2px;
        margin: 0 auto var(--sc-space-lg);
      }

      /* Header */
      .detail-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: var(--sc-space-lg);
      }

      .detail-title {
        font-size: var(--sc-font-xl);
        font-weight: 700;
        color: var(--sc-text-primary);
      }

      .detail-close {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: var(--sc-tile-bg);
        border: 1px solid var(--sc-tile-border);
        color: var(--sc-text-secondary);
        font-size: var(--sc-font-lg);
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: background 0.2s;
      }

      .detail-close:hover {
        background: var(--sc-tile-bg-hover);
      }

      /* Sections */
      .detail-section {
        margin-bottom: var(--sc-space-lg);
      }

      .detail-section-title {
        font-size: var(--sc-font-sm);
        font-weight: 600;
        color: var(--sc-text-muted);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: var(--sc-space-sm);
      }

      /* Big temp display */
      .detail-temp-display {
        display: flex;
        align-items: baseline;
        gap: var(--sc-space-sm);
        margin-bottom: var(--sc-space-md);
      }

      .detail-temp-value {
        font-size: 3rem;
        font-weight: 700;
        line-height: 1;
        color: var(--sc-text-primary);
      }

      .detail-temp-unit {
        font-size: var(--sc-font-lg);
        color: var(--sc-text-muted);
      }

      .detail-temp-trend {
        font-size: var(--sc-font-xl);
        color: var(--sc-text-secondary);
      }

      /* Stats grid */
      .detail-stats {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: var(--sc-space-sm);
      }

      .detail-stat {
        background: var(--sc-tile-bg);
        border: 1px solid var(--sc-tile-border);
        border-radius: var(--sc-radius-md);
        padding: var(--sc-space-sm) var(--sc-space-md);
      }

      .detail-stat-label {
        font-size: var(--sc-font-xs);
        color: var(--sc-text-muted);
        margin-bottom: 2px;
      }

      .detail-stat-value {
        font-size: var(--sc-font-lg);
        font-weight: 600;
        color: var(--sc-text-primary);
      }

      .detail-stat-sub {
        font-size: var(--sc-font-xs);
        color: var(--sc-text-secondary);
      }

      /* Comfort/efficiency bars */
      .detail-bar-row {
        display: flex;
        align-items: center;
        gap: var(--sc-space-sm);
        margin-bottom: var(--sc-space-sm);
      }

      .detail-bar-label {
        font-size: var(--sc-font-sm);
        color: var(--sc-text-secondary);
        min-width: 80px;
      }

      .detail-bar {
        flex: 1;
        height: 8px;
        background: rgba(255, 255, 255, 0.06);
        border-radius: 4px;
        overflow: hidden;
      }

      .detail-bar-fill {
        height: 100%;
        border-radius: 4px;
        transition: width 0.6s ease;
      }

      .detail-bar-value {
        font-size: var(--sc-font-sm);
        font-weight: 600;
        min-width: 40px;
        text-align: right;
      }

      /* Climate controls */
      .detail-controls {
        display: flex;
        flex-direction: column;
        gap: var(--sc-space-md);
      }

      .control-row {
        display: flex;
        align-items: center;
        gap: var(--sc-space-md);
      }

      .control-label {
        font-size: var(--sc-font-sm);
        color: var(--sc-text-secondary);
        min-width: 80px;
      }

      .temp-control {
        display: flex;
        align-items: center;
        gap: var(--sc-space-sm);
      }

      .temp-btn {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: var(--sc-tile-bg);
        border: 1px solid var(--sc-tile-border);
        color: var(--sc-text-primary);
        font-size: var(--sc-font-lg);
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: background 0.2s;
        user-select: none;
      }

      .temp-btn:hover {
        background: var(--sc-tile-bg-hover);
      }

      .temp-btn:active {
        transform: scale(0.93);
      }

      .temp-display {
        font-size: var(--sc-font-xl);
        font-weight: 600;
        color: var(--sc-text-primary);
        min-width: 60px;
        text-align: center;
      }

      /* Mode select */
      .mode-select {
        display: flex;
        gap: var(--sc-space-xs);
      }

      .mode-btn {
        padding: var(--sc-space-xs) var(--sc-space-md);
        border-radius: var(--sc-radius-sm);
        background: var(--sc-tile-bg);
        border: 1px solid var(--sc-tile-border);
        color: var(--sc-text-secondary);
        font-size: var(--sc-font-xs);
        cursor: pointer;
        transition: background 0.2s, color 0.2s;
      }

      .mode-btn:hover {
        background: var(--sc-tile-bg-hover);
      }

      .mode-btn.active {
        background: rgba(33, 150, 243, 0.2);
        border-color: rgba(33, 150, 243, 0.4);
        color: #64b5f6;
      }

      /* Device list */
      .device-list {
        display: flex;
        flex-direction: column;
        gap: var(--sc-space-xs);
      }

      .device-item {
        display: flex;
        align-items: center;
        gap: var(--sc-space-sm);
        padding: var(--sc-space-sm);
        background: var(--sc-tile-bg);
        border-radius: var(--sc-radius-sm);
        font-size: var(--sc-font-sm);
        color: var(--sc-text-secondary);
      }

      .device-icon {
        font-size: var(--sc-font-md);
      }

      .device-name {
        flex: 1;
        color: var(--sc-text-primary);
      }

      .device-state {
        font-size: var(--sc-font-xs);
        color: var(--sc-text-muted);
      }

      /* Vent status */
      .vent-status {
        display: flex;
        align-items: center;
        gap: var(--sc-space-sm);
        padding: var(--sc-space-sm);
        background: var(--sc-tile-bg);
        border-radius: var(--sc-radius-sm);
      }

      .vent-icon {
        font-size: var(--sc-font-lg);
      }

      .vent-info {
        flex: 1;
      }

      .vent-name {
        font-size: var(--sc-font-sm);
        color: var(--sc-text-primary);
      }

      .vent-position {
        font-size: var(--sc-font-xs);
        color: var(--sc-text-muted);
      }
    `,
  ];

  private _entity(suffix: string): HassEntity | undefined {
    return getEntityState(this.hass, `sensor.sc_${this.roomSlug}_${suffix}`);
  }

  private _binaryEntity(suffix: string): HassEntity | undefined {
    return getEntityState(
      this.hass,
      `binary_sensor.sc_${this.roomSlug}_${suffix}`,
    );
  }

  private _close() {
    this.dispatchEvent(
      new CustomEvent('room-detail-close', {
        bubbles: true,
        composed: true,
      }),
    );
  }

  private _handleOverlayClick(e: Event) {
    if ((e.target as HTMLElement).classList.contains('detail-overlay')) {
      this._close();
    }
  }

  private _adjustTarget(delta: number) {
    this._targetTemp = Math.round((this._targetTemp + delta) * 2) / 2;
    callService(this.hass, 'smart_climate', 'set_target_temperature', {
      room: this.roomSlug,
      temperature: this._targetTemp,
    }).catch((err: unknown) =>
      console.error('Failed to set target temperature:', err),
    );
  }

  private _setMode(mode: string) {
    this._hvacMode = mode;
    callService(this.hass, 'smart_climate', 'set_hvac_mode', {
      room: this.roomSlug,
      mode,
    }).catch((err: unknown) =>
      console.error('Failed to set HVAC mode:', err),
    );
  }

  updated(changedProps: Map<string, unknown>) {
    if (changedProps.has('roomSlug') || changedProps.has('open')) {
      // Sync target temp from entity when opening
      const targetEntity = this._entity('target_temperature');
      if (targetEntity) {
        const val = parseFloat(targetEntity.state);
        if (!isNaN(val)) this._targetTemp = val;
      }
      // Sync HVAC mode
      const modeEntity = this._entity('hvac_mode');
      if (modeEntity && modeEntity.state !== 'unknown') {
        this._hvacMode = modeEntity.state;
      }
    }
  }

  render() {
    if (!this.open || !this.roomSlug) return nothing;

    const comfortEntity = this._entity('comfort_score');
    const efficiencyEntity = this._entity('efficiency');
    const tempEntity = this._entity('temperature');
    const humidityEntity = this._entity('humidity');
    const trendEntity = this._entity('temperature_trend');
    const hvacEntity = this._entity('hvac_action');
    const runtimeEntity = this._entity('hvac_runtime');
    const scheduleEntity = this._entity('active_schedule');
    const ventEntity = this._entity('vent_position');
    const auxEntity = this._entity('auxiliary');

    const comfortScore = comfortEntity ? parseFloat(comfortEntity.state) : NaN;
    const efficiencyScore = efficiencyEntity
      ? parseFloat(efficiencyEntity.state)
      : NaN;
    const temp = tempEntity?.state;
    const humidity = humidityEntity?.state;
    const trend = trendEntity?.state;
    const hvacAction = hvacEntity?.state || 'idle';
    const runtime = runtimeEntity?.state;
    const schedule = scheduleEntity?.state || 'None';
    const tempUnit = tempEntity?.attributes?.unit_of_measurement || '°F';

    // Vent info
    const ventPosition = ventEntity?.state;
    const ventName = ventEntity?.attributes?.friendly_name || 'Vent';

    // Auxiliary devices
    const auxDevices: Array<{
      name: string;
      type: string;
      state: string;
      runtime: number;
    }> = auxEntity?.attributes?.devices || [];

    // Sensor list from attributes
    const sensors: Array<{ name: string; entity_id: string; state: string }> =
      comfortEntity?.attributes?.sensors || [];

    const hvacModes = ['auto', 'heat', 'cool', 'fan_only', 'off'];

    return html`
      <div class="detail-overlay" @click=${this._handleOverlayClick}>
        <div class="detail-drawer">
          <!-- Handle -->
          <div class="detail-handle"></div>

          <!-- Header -->
          <div class="detail-header">
            <span class="detail-title">${getRoomName(this.roomSlug)}</span>
            <button class="detail-close" @click=${this._close}>&times;</button>
          </div>

          <!-- Temperature display -->
          <div class="detail-section">
            <div class="detail-temp-display">
              <span class="detail-temp-value">${formatTemp(temp, '')}</span>
              <span class="detail-temp-unit">${tempUnit}</span>
              <span class="detail-temp-trend">${getTrendArrow(trend)}</span>
            </div>
          </div>

          <!-- Stats grid -->
          <div class="detail-section">
            <div class="detail-stats">
              <div class="detail-stat">
                <div class="detail-stat-label">Humidity</div>
                <div class="detail-stat-value">
                  ${humidity && humidity !== 'unknown'
                    ? `${Math.round(parseFloat(humidity))}%`
                    : '--'}
                </div>
              </div>
              <div class="detail-stat">
                <div class="detail-stat-label">HVAC</div>
                <div class="detail-stat-value" style="color: ${getHvacColor(hvacAction)}">
                  ${getHvacIcon(hvacAction)}
                  ${hvacAction.charAt(0).toUpperCase() + hvacAction.slice(1)}
                </div>
                <div class="detail-stat-sub">Runtime: ${formatDuration(runtime)}</div>
              </div>
              <div class="detail-stat">
                <div class="detail-stat-label">Schedule</div>
                <div class="detail-stat-value">${schedule}</div>
              </div>
              <div class="detail-stat">
                <div class="detail-stat-label">Target</div>
                <div class="detail-stat-value">${formatTemp(this._targetTemp, tempUnit)}</div>
              </div>
            </div>
          </div>

          <!-- Comfort / Efficiency bars -->
          <div class="detail-section">
            <div class="detail-section-title">Performance</div>

            <div class="detail-bar-row">
              <span class="detail-bar-label">Comfort</span>
              <div class="detail-bar">
                <div
                  class="detail-bar-fill"
                  style="width: ${!isNaN(comfortScore) ? comfortScore : 0}%; background: ${getComfortColor(comfortScore)}"
                ></div>
              </div>
              <span class="detail-bar-value" style="color: ${getComfortColor(comfortScore)}">
                ${formatScore(comfortScore)}
              </span>
            </div>

            <div class="detail-bar-row">
              <span class="detail-bar-label">Efficiency</span>
              <div class="detail-bar">
                <div
                  class="detail-bar-fill"
                  style="width: ${!isNaN(efficiencyScore) ? efficiencyScore : 0}%; background: ${getComfortColor(efficiencyScore)}"
                ></div>
              </div>
              <span class="detail-bar-value" style="color: ${getComfortColor(efficiencyScore)}">
                ${formatScore(efficiencyScore)}
              </span>
            </div>

            <!-- Efficiency chart -->
            <efficiency-chart
              .hass=${this.hass}
              .roomSlug=${this.roomSlug}
            ></efficiency-chart>
          </div>

          <!-- Climate controls -->
          <div class="detail-section">
            <div class="detail-section-title">Climate Control</div>
            <div class="detail-controls">
              <!-- Target temperature -->
              <div class="control-row">
                <span class="control-label">Target</span>
                <div class="temp-control">
                  <button class="temp-btn" @click=${() => this._adjustTarget(-0.5)}>-</button>
                  <span class="temp-display">${formatTemp(this._targetTemp, tempUnit)}</span>
                  <button class="temp-btn" @click=${() => this._adjustTarget(0.5)}>+</button>
                </div>
              </div>

              <!-- Mode select -->
              <div class="control-row">
                <span class="control-label">Mode</span>
                <div class="mode-select">
                  ${hvacModes.map(
                    (mode) => html`
                      <button
                        class="mode-btn ${this._hvacMode === mode ? 'active' : ''}"
                        @click=${() => this._setMode(mode)}
                      >
                        ${mode.replace('_', ' ')}
                      </button>
                    `,
                  )}
                </div>
              </div>
            </div>
          </div>

          <!-- Vent status -->
          ${ventPosition &&
          ventPosition !== 'unknown' &&
          ventPosition !== 'unavailable'
            ? html`
                <div class="detail-section">
                  <div class="detail-section-title">Vent</div>
                  <div class="vent-status">
                    <span class="vent-icon">🔲</span>
                    <div class="vent-info">
                      <div class="vent-name">${ventName}</div>
                      <div class="vent-position">Position: ${ventPosition}%</div>
                    </div>
                  </div>
                </div>
              `
            : nothing}

          <!-- Auxiliary devices -->
          ${auxDevices.length > 0
            ? html`
                <div class="detail-section">
                  <div class="detail-section-title">Auxiliary Devices</div>
                  <div class="device-list">
                    ${auxDevices.map(
                      (device) => html`
                        <div class="device-item">
                          <span class="device-icon">
                            ${device.state === 'on' || device.state === 'active'
                              ? '🟢'
                              : '⚫'}
                          </span>
                          <span class="device-name">${device.name}</span>
                          <span class="device-state">${device.state}</span>
                        </div>
                      `,
                    )}
                  </div>
                </div>
              `
            : nothing}

          <!-- Sensor list -->
          ${sensors.length > 0
            ? html`
                <div class="detail-section">
                  <div class="detail-section-title">Sensors</div>
                  <div class="device-list">
                    ${sensors.map(
                      (sensor) => html`
                        <div class="device-item">
                          <span class="device-icon">📡</span>
                          <span class="device-name">${sensor.name}</span>
                          <span class="device-state">${sensor.state}</span>
                        </div>
                      `,
                    )}
                  </div>
                </div>
              `
            : nothing}
        </div>
      </div>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'room-detail': RoomDetail;
  }
}
