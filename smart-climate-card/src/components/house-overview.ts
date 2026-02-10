import { LitElement, html, css, nothing } from 'lit';
import { customElement, property } from 'lit/decorators.js';
import { themeStyles } from '../styles/theme';
import { animationStyles } from '../styles/animations';
import type { HomeAssistant } from '../utils/ha-api';
import { getEntityState } from '../utils/ha-api';
import {
  formatScore,
  getComfortColor,
  getComfortLabel,
  getHvacIcon,
  getHvacColor,
} from '../utils/formatters';

/**
 * <house-overview> component
 * Header bar with house comfort/efficiency scores, HVAC status, follow-me status, active schedule.
 */
@customElement('house-overview')
export class HouseOverview extends LitElement {
  @property({ attribute: false }) hass!: HomeAssistant;

  static styles = [
    themeStyles,
    animationStyles,
    css`
      :host {
        display: block;
      }

      .overview {
        display: flex;
        flex-direction: column;
        gap: var(--sc-space-md);
        padding-bottom: var(--sc-space-md);
      }

      /* Title row */
      .overview-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
      }

      .overview-title {
        font-size: var(--sc-font-lg);
        font-weight: 700;
        color: var(--sc-text-primary);
        letter-spacing: -0.3px;
      }

      .overview-subtitle {
        font-size: var(--sc-font-xs);
        color: var(--sc-text-muted);
        margin-top: 2px;
      }

      /* Scores row */
      .overview-scores {
        display: flex;
        gap: var(--sc-space-md);
        flex-wrap: wrap;
      }

      .score-block {
        flex: 1;
        min-width: 100px;
        background: var(--sc-tile-bg);
        border: 1px solid var(--sc-tile-border);
        border-radius: var(--sc-radius-md);
        padding: var(--sc-space-sm) var(--sc-space-md);
      }

      .score-label {
        font-size: var(--sc-font-xs);
        color: var(--sc-text-muted);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: var(--sc-space-xs);
      }

      .score-value {
        font-size: var(--sc-font-xl);
        font-weight: 700;
        line-height: 1;
      }

      .score-sublabel {
        font-size: var(--sc-font-xs);
        color: var(--sc-text-secondary);
        margin-top: 2px;
      }

      /* Segmented progress bar */
      .progress-segmented {
        display: flex;
        gap: 2px;
        height: 4px;
        margin-top: var(--sc-space-sm);
      }

      .progress-segment {
        flex: 1;
        border-radius: 2px;
        transition: background-color 0.3s ease;
      }

      /* Status row */
      .overview-status {
        display: flex;
        flex-wrap: wrap;
        gap: var(--sc-space-sm);
      }

      .status-chip {
        display: inline-flex;
        align-items: center;
        gap: var(--sc-space-xs);
        padding: var(--sc-space-xs) var(--sc-space-sm);
        background: var(--sc-tile-bg);
        border: 1px solid var(--sc-tile-border);
        border-radius: var(--sc-radius-xl);
        font-size: var(--sc-font-xs);
        color: var(--sc-text-secondary);
        white-space: nowrap;
      }

      .status-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        flex-shrink: 0;
      }

      .status-label {
        font-weight: 500;
      }
    `,
  ];

  private _getComfort() {
    return getEntityState(this.hass, 'sensor.sc_house_comfort');
  }

  private _getEfficiency() {
    return getEntityState(this.hass, 'sensor.sc_house_efficiency');
  }

  private _getSchedule() {
    return getEntityState(this.hass, 'sensor.sc_active_schedule');
  }

  private _getHvacStatus() {
    return getEntityState(this.hass, 'sensor.sc_hvac_status');
  }

  private _getFollowMe() {
    return getEntityState(this.hass, 'binary_sensor.sc_follow_me_active');
  }

  private _renderSegmentedBar(score: number) {
    const segments = 10;
    const filledSegments = Math.round((score / 100) * segments);
    const color = getComfortColor(score);

    return html`
      <div class="progress-segmented">
        ${Array.from({ length: segments }).map(
          (_, i) => html`
            <div
              class="progress-segment"
              style="background: ${i < filledSegments
                ? color
                : 'rgba(255,255,255,0.06)'}"
            ></div>
          `,
        )}
      </div>
    `;
  }

  render() {
    const comfort = this._getComfort();
    const efficiency = this._getEfficiency();
    const schedule = this._getSchedule();
    const hvac = this._getHvacStatus();
    const followMe = this._getFollowMe();

    const comfortScore = comfort ? parseFloat(comfort.state) : NaN;
    const efficiencyScore = efficiency ? parseFloat(efficiency.state) : NaN;
    const hvacAction = hvac?.state || 'idle';
    const followMeActive = followMe?.state === 'on';
    const followMeTarget = followMe?.attributes?.target_room || '';
    const scheduleName = schedule?.state || 'None';

    return html`
      <div class="overview">
        <!-- Title -->
        <div class="overview-header">
          <div>
            <div class="overview-title">Smart Climate</div>
            <div class="overview-subtitle">Whole-house overview</div>
          </div>
        </div>

        <!-- Score blocks -->
        <div class="overview-scores">
          <div class="score-block">
            <div class="score-label">Comfort</div>
            <div
              class="score-value"
              style="color: ${getComfortColor(comfortScore)}"
            >
              ${formatScore(comfortScore)}
            </div>
            <div class="score-sublabel">${getComfortLabel(comfortScore)}</div>
            ${!isNaN(comfortScore) ? this._renderSegmentedBar(comfortScore) : nothing}
          </div>

          <div class="score-block">
            <div class="score-label">Efficiency</div>
            <div
              class="score-value"
              style="color: ${getComfortColor(efficiencyScore)}"
            >
              ${formatScore(efficiencyScore)}
            </div>
            <div class="score-sublabel">
              ${!isNaN(efficiencyScore) ? `${Math.round(efficiencyScore)}%` : '--'}
            </div>
            ${!isNaN(efficiencyScore) ? this._renderSegmentedBar(efficiencyScore) : nothing}
          </div>
        </div>

        <!-- Status chips -->
        <div class="overview-status">
          <!-- HVAC Status -->
          <div class="status-chip">
            <div
              class="status-dot ${hvacAction !== 'idle' && hvacAction !== 'off'
                ? 'sc-dot-pulse'
                : ''}"
              style="background: ${getHvacColor(hvacAction)}"
            ></div>
            <span>${getHvacIcon(hvacAction)}</span>
            <span class="status-label"
              >HVAC: ${hvacAction.charAt(0).toUpperCase() + hvacAction.slice(1)}</span
            >
          </div>

          <!-- Follow-Me -->
          ${followMeActive
            ? html`
                <div class="status-chip">
                  <div
                    class="status-dot sc-dot-pulse"
                    style="background: var(--sc-comfort-good)"
                  ></div>
                  <span class="status-label">Follow-Me: ${followMeTarget}</span>
                </div>
              `
            : nothing}

          <!-- Active Schedule -->
          <div class="status-chip">
            <span class="status-label">Schedule: ${scheduleName}</span>
          </div>
        </div>
      </div>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'house-overview': HouseOverview;
  }
}
