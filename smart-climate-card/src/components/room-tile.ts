import { LitElement, html, css, nothing } from 'lit';
import { customElement, property } from 'lit/decorators.js';
import { themeStyles } from '../styles/theme';
import { animationStyles } from '../styles/animations';
import type { HomeAssistant, HassEntity } from '../utils/ha-api';
import { getEntityState, getRoomName } from '../utils/ha-api';
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
 * <room-tile> component
 * Displays a single room's climate status as a compact tile in the grid.
 */
@customElement('room-tile')
export class RoomTile extends LitElement {
  @property({ attribute: false }) hass!: HomeAssistant;
  @property({ type: String }) roomSlug: string = '';
  @property({ type: Boolean }) compact: boolean = false;

  static styles = [
    themeStyles,
    animationStyles,
    css`
      :host {
        display: block;
      }

      .tile {
        position: relative;
        background: var(--sc-tile-bg);
        border: 1px solid var(--sc-tile-border);
        border-radius: var(--sc-tile-radius);
        padding: var(--sc-space-md);
        cursor: pointer;
        transition: background 0.2s ease, box-shadow 0.3s ease,
          transform 0.15s ease;
        overflow: hidden;
      }

      .tile:hover {
        background: var(--sc-tile-bg-hover);
        transform: translateY(-1px);
      }

      .tile:active {
        transform: scale(0.98);
      }

      /* Gradient overlay based on comfort score */
      .tile-gradient {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        opacity: 0.06;
        pointer-events: none;
        border-radius: var(--sc-tile-radius);
        transition: opacity 0.3s ease;
      }

      .tile:hover .tile-gradient {
        opacity: 0.1;
      }

      /* Occupied glow */
      .tile.occupied {
        box-shadow: var(--sc-glow-occupied);
      }

      /* Follow-me glow */
      .tile.follow-me {
        box-shadow: var(--sc-glow-followme);
        border-color: rgba(33, 150, 243, 0.3);
      }

      /* Header: room name + occupancy */
      .tile-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: var(--sc-space-sm);
      }

      .tile-name {
        font-size: var(--sc-font-md);
        font-weight: 600;
        color: var(--sc-text-primary);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }

      .tile-occupancy {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        flex-shrink: 0;
        background: var(--sc-comfort-fair);
      }

      .tile-occupancy.vacant {
        background: var(--sc-text-muted);
        opacity: 0.4;
      }

      /* Temperature display */
      .tile-temp-row {
        display: flex;
        align-items: baseline;
        gap: var(--sc-space-xs);
        margin-bottom: var(--sc-space-xs);
      }

      .tile-temp {
        font-size: var(--sc-font-xxl);
        font-weight: 700;
        line-height: 1;
        color: var(--sc-text-primary);
      }

      .tile-trend {
        font-size: var(--sc-font-md);
        color: var(--sc-text-secondary);
      }

      .tile-unit {
        font-size: var(--sc-font-sm);
        color: var(--sc-text-muted);
        font-weight: 400;
      }

      /* Secondary stats row */
      .tile-stats {
        display: flex;
        align-items: center;
        gap: var(--sc-space-md);
        margin-bottom: var(--sc-space-sm);
        font-size: var(--sc-font-xs);
        color: var(--sc-text-secondary);
      }

      .tile-stat {
        display: flex;
        align-items: center;
        gap: 3px;
      }

      .tile-stat-icon {
        opacity: 0.6;
      }

      /* Comfort bar */
      .tile-comfort {
        margin-bottom: var(--sc-space-sm);
      }

      .tile-comfort-label {
        display: flex;
        justify-content: space-between;
        font-size: var(--sc-font-xs);
        color: var(--sc-text-muted);
        margin-bottom: 3px;
      }

      .tile-comfort-bar {
        width: 100%;
        height: 4px;
        background: rgba(255, 255, 255, 0.06);
        border-radius: 2px;
        overflow: hidden;
      }

      .tile-comfort-fill {
        height: 100%;
        border-radius: 2px;
        transition: width 0.6s ease, background-color 0.3s ease;
      }

      /* HVAC action row */
      .tile-hvac {
        display: flex;
        align-items: center;
        gap: var(--sc-space-xs);
        font-size: var(--sc-font-xs);
        color: var(--sc-text-secondary);
        margin-bottom: var(--sc-space-xs);
      }

      .tile-hvac-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        flex-shrink: 0;
      }

      .tile-hvac-text {
        flex: 1;
      }

      .tile-hvac-runtime {
        color: var(--sc-text-muted);
      }

      /* Schedule label */
      .tile-schedule {
        font-size: var(--sc-font-xs);
        color: var(--sc-text-muted);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        margin-bottom: var(--sc-space-xs);
      }

      /* Auxiliary slot */
      .tile-auxiliary {
        margin-top: var(--sc-space-xs);
      }

      /* Compact mode */
      :host([compact]) .tile {
        padding: var(--sc-space-sm);
      }

      :host([compact]) .tile-temp {
        font-size: var(--sc-font-xl);
      }

      :host([compact]) .tile-stats {
        display: none;
      }

      :host([compact]) .tile-schedule {
        display: none;
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

  private _handleClick() {
    this.dispatchEvent(
      new CustomEvent('room-detail-open', {
        detail: { roomSlug: this.roomSlug },
        bubbles: true,
        composed: true,
      }),
    );
  }

  render() {
    const comfortEntity = this._entity('comfort_score');
    const tempEntity = this._entity('temperature');
    const humidityEntity = this._entity('humidity');
    const targetEntity = this._entity('target_temperature');
    const trendEntity = this._entity('temperature_trend');
    const hvacEntity = this._entity('hvac_action');
    const runtimeEntity = this._entity('hvac_runtime');
    const scheduleEntity = this._entity('active_schedule');
    const occupancyEntity = this._binaryEntity('occupancy');
    const followMeEntity = this._binaryEntity('follow_me_target');

    const comfortScore = comfortEntity ? parseFloat(comfortEntity.state) : NaN;
    const temp = tempEntity?.state;
    const humidity = humidityEntity?.state;
    const target = targetEntity?.state;
    const trend = trendEntity?.state;
    const hvacAction = hvacEntity?.state || 'idle';
    const runtime = runtimeEntity?.state;
    const schedule = scheduleEntity?.state || '';
    const occupied = occupancyEntity?.state === 'on';
    const isFollowMe = followMeEntity?.state === 'on';

    const comfortColor = getComfortColor(comfortScore);
    const comfortPct = !isNaN(comfortScore) ? Math.max(0, Math.min(100, comfortScore)) : 0;

    const tempUnit = tempEntity?.attributes?.unit_of_measurement || '°F';

    const tileClasses = [
      'tile',
      occupied ? 'occupied' : '',
      isFollowMe ? 'follow-me' : '',
    ]
      .filter(Boolean)
      .join(' ');

    return html`
      <div class="${tileClasses}" @click=${this._handleClick}>
        <!-- Comfort gradient overlay -->
        <div
          class="tile-gradient"
          style="background: radial-gradient(circle at top left, ${comfortColor}, transparent 70%)"
        ></div>

        <!-- Header: name + occupancy -->
        <div class="tile-header">
          <span class="tile-name">${getRoomName(this.roomSlug)}</span>
          <span
            class="tile-occupancy ${occupied ? '' : 'vacant'}"
            title="${occupied ? 'Occupied' : 'Vacant'}"
          ></span>
        </div>

        <!-- Temperature -->
        <div class="tile-temp-row">
          <span class="tile-temp">${formatTemp(temp, '')}</span>
          <span class="tile-unit">${tempUnit}</span>
          <span class="tile-trend">${getTrendArrow(trend)}</span>
        </div>

        <!-- Secondary stats: humidity, target -->
        <div class="tile-stats">
          <span class="tile-stat">
            <span class="tile-stat-icon">💧</span>
            ${humidity !== undefined && humidity !== 'unknown'
              ? `${Math.round(parseFloat(humidity as string))}%`
              : '--'}
          </span>
          <span class="tile-stat">
            <span class="tile-stat-icon">🎯</span>
            ${formatTemp(target, tempUnit)}
          </span>
        </div>

        <!-- Comfort bar -->
        <div class="tile-comfort">
          <div class="tile-comfort-label">
            <span>Comfort</span>
            <span style="color: ${comfortColor}">
              ${formatScore(comfortScore)} - ${getComfortLabel(comfortScore)}
            </span>
          </div>
          <div class="tile-comfort-bar">
            <div
              class="tile-comfort-fill"
              style="width: ${comfortPct}%; background: ${comfortColor}"
            ></div>
          </div>
        </div>

        <!-- HVAC action -->
        <div class="tile-hvac">
          <div
            class="tile-hvac-dot ${hvacAction !== 'idle' && hvacAction !== 'off'
              ? 'sc-dot-pulse'
              : ''}"
            style="background: ${getHvacColor(hvacAction)}"
          ></div>
          <span class="tile-hvac-text">
            ${getHvacIcon(hvacAction)}
            ${hvacAction.charAt(0).toUpperCase() + hvacAction.slice(1)}
          </span>
          <span class="tile-hvac-runtime">${formatDuration(runtime)}</span>
        </div>

        <!-- Schedule -->
        ${schedule && schedule !== 'unknown' && schedule !== 'unavailable'
          ? html`<div class="tile-schedule">📅 ${schedule}</div>`
          : nothing}

        <!-- Auxiliary devices slot -->
        <div class="tile-auxiliary">
          <auxiliary-status
            .hass=${this.hass}
            .roomSlug=${this.roomSlug}
          ></auxiliary-status>
        </div>
      </div>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'room-tile': RoomTile;
  }
}
