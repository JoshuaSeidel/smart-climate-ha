import { LitElement, html, css, nothing } from 'lit';
import { customElement, property } from 'lit/decorators.js';
import { themeStyles } from '../styles/theme';
import { animationStyles } from '../styles/animations';
import type { HomeAssistant } from '../utils/ha-api';
import { getEntityState } from '../utils/ha-api';
import { formatDuration } from '../utils/formatters';

/**
 * <auxiliary-status> component
 * Shows auxiliary device status for a room: which devices are on, reason, runtime.
 * Only renders when auxiliary is active.
 */
@customElement('auxiliary-status')
export class AuxiliaryStatus extends LitElement {
  @property({ attribute: false }) hass!: HomeAssistant;
  @property({ type: String }) roomSlug: string = '';

  static styles = [
    themeStyles,
    animationStyles,
    css`
      :host {
        display: block;
      }

      .aux-container {
        display: flex;
        flex-direction: column;
        gap: var(--sc-space-xs);
      }

      .aux-device {
        display: flex;
        align-items: center;
        gap: var(--sc-space-sm);
        padding: var(--sc-space-xs) var(--sc-space-sm);
        background: rgba(255, 255, 255, 0.04);
        border-radius: var(--sc-radius-sm);
        font-size: var(--sc-font-xs);
      }

      .aux-icon {
        font-size: var(--sc-font-md);
        flex-shrink: 0;
      }

      .aux-info {
        flex: 1;
        min-width: 0;
      }

      .aux-name {
        color: var(--sc-text-primary);
        font-weight: 500;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }

      .aux-detail {
        color: var(--sc-text-muted);
        font-size: var(--sc-font-xs);
      }

      .aux-status-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        flex-shrink: 0;
      }

      .aux-status-dot.on {
        background: var(--sc-comfort-excellent);
      }

      .aux-status-dot.off {
        background: var(--sc-hvac-idle);
      }

      .aux-runtime {
        color: var(--sc-text-muted);
        font-size: var(--sc-font-xs);
        flex-shrink: 0;
      }

      .aux-reason {
        color: var(--sc-text-secondary);
        font-size: var(--sc-font-xs);
        font-style: italic;
        padding-left: var(--sc-space-sm);
        margin-top: 2px;
      }
    `,
  ];

  private _getAuxEntity() {
    return getEntityState(this.hass, `sensor.sc_${this.roomSlug}_auxiliary`);
  }

  private _getDeviceIcon(deviceType: string): string {
    switch (deviceType?.toLowerCase()) {
      case 'fan':
      case 'ceiling_fan':
        return '🌀';
      case 'humidifier':
        return '💨';
      case 'dehumidifier':
        return '🌊';
      case 'heater':
      case 'space_heater':
        return '🔥';
      case 'air_purifier':
        return '🌿';
      case 'window':
        return '🪟';
      default:
        return '⚡';
    }
  }

  render() {
    const auxEntity = this._getAuxEntity();
    if (!auxEntity) return nothing;

    const devices: Array<{
      name: string;
      type: string;
      state: string;
      runtime: number;
      reason: string;
    }> = auxEntity.attributes?.devices || [];

    const activeDevices = devices.filter(
      (d) => d.state === 'on' || d.state === 'active',
    );

    if (activeDevices.length === 0) return nothing;

    return html`
      <div class="aux-container">
        ${activeDevices.map(
          (device) => html`
            <div class="aux-device sc-fade-in">
              <span class="aux-icon">${this._getDeviceIcon(device.type)}</span>
              <div class="aux-info">
                <div class="aux-name">${device.name}</div>
                ${device.reason
                  ? html`<div class="aux-reason">${device.reason}</div>`
                  : nothing}
              </div>
              <span class="aux-runtime">${formatDuration(device.runtime)}</span>
              <span class="aux-status-dot on sc-dot-pulse"></span>
            </div>
          `,
        )}
      </div>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'auxiliary-status': AuxiliaryStatus;
  }
}
