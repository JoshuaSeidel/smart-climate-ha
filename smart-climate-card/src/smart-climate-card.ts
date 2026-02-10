import { LitElement, html, css, nothing, PropertyValues } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';

// Sub-components
import './components/room-tile';
import './components/house-overview';
import './components/suggestion-panel';
import './components/schedule-view';
import './components/room-detail';
import './components/efficiency-chart';
import './components/auxiliary-status';

// Styles
import { themeStyles } from './styles/theme';
import { cardStyles } from './styles/card-styles';
import { animationStyles } from './styles/animations';

// Utilities
import type { HomeAssistant } from './utils/ha-api';
import { discoverRooms } from './utils/ha-api';

/**
 * Card configuration interface.
 */
interface SmartClimateCardConfig {
  entity?: string;
  show_schedule?: boolean;
  show_suggestions?: boolean;
  show_efficiency?: boolean;
  columns?: number;
  compact?: boolean;
  rooms_order?: string[];
}

/**
 * Smart Climate Card - Main Lovelace card element.
 *
 * Provides a complete dashboard view of the Smart Climate integration:
 * - House overview with comfort/efficiency scores
 * - Responsive room grid with climate tiles
 * - Collapsible schedule timeline
 * - AI suggestion panel with approve/reject controls
 */
@customElement('smart-climate-card')
export class SmartClimateCard extends LitElement {
  // Home Assistant instance, set by Lovelace
  @property({ attribute: false }) hass!: HomeAssistant;

  // Card configuration
  @state() private _config: SmartClimateCardConfig = {};

  // Discovered rooms
  @state() private _rooms: string[] = [];

  // Room detail drawer state
  @state() private _detailRoom: string = '';
  @state() private _detailOpen: boolean = false;

  static styles = [
    themeStyles,
    cardStyles,
    animationStyles,
    css`
      :host {
        display: block;
      }

      .sc-card {
        background: var(--sc-card-bg);
        backdrop-filter: var(--sc-backdrop-blur);
        -webkit-backdrop-filter: var(--sc-backdrop-blur);
        border: 1px solid var(--sc-card-border);
        border-radius: var(--sc-radius-xl);
        box-shadow: var(--sc-card-shadow);
        padding: var(--sc-space-lg);
        overflow: hidden;
      }

      /* Grid column overrides */
      .sc-room-grid.cols-1 {
        grid-template-columns: 1fr;
      }

      .sc-room-grid.cols-2 {
        grid-template-columns: repeat(2, 1fr);
      }

      .sc-room-grid.cols-3 {
        grid-template-columns: repeat(3, 1fr);
      }

      @media (max-width: 500px) {
        .sc-room-grid.cols-2,
        .sc-room-grid.cols-3 {
          grid-template-columns: 1fr;
        }
      }

      @media (min-width: 501px) and (max-width: 800px) {
        .sc-room-grid.cols-3 {
          grid-template-columns: repeat(2, 1fr);
        }
      }

      /* Rooms section label */
      .sc-rooms-label {
        font-size: var(--sc-font-sm);
        font-weight: 600;
        color: var(--sc-text-muted);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: var(--sc-space-sm);
        margin-top: var(--sc-space-md);
      }
    `,
  ];

  /**
   * Set card configuration from the Lovelace UI editor or YAML.
   */
  setConfig(config: SmartClimateCardConfig) {
    this._config = {
      show_schedule: true,
      show_suggestions: true,
      show_efficiency: true,
      compact: false,
      ...config,
    };
  }

  /**
   * Return the card size for Lovelace layout calculations.
   */
  getCardSize(): number {
    return 6;
  }

  /**
   * Static config stub for the card picker (editor).
   */
  static getStubConfig(): SmartClimateCardConfig {
    return {
      show_schedule: true,
      show_suggestions: true,
      show_efficiency: true,
      compact: false,
    };
  }

  /**
   * Discover rooms whenever hass updates.
   */
  updated(changedProps: PropertyValues) {
    super.updated(changedProps);

    if (changedProps.has('hass') && this.hass) {
      this._discoverRooms();
    }
  }

  private _discoverRooms() {
    const discovered = discoverRooms(this.hass);

    // Apply rooms_order from config if specified
    if (this._config.rooms_order && this._config.rooms_order.length > 0) {
      const ordered: string[] = [];
      for (const slug of this._config.rooms_order) {
        if (discovered.includes(slug)) {
          ordered.push(slug);
        }
      }
      // Append any discovered rooms not in the order list
      for (const slug of discovered) {
        if (!ordered.includes(slug)) {
          ordered.push(slug);
        }
      }
      this._rooms = ordered;
    } else {
      this._rooms = discovered;
    }
  }

  private _handleRoomDetailOpen(e: CustomEvent) {
    this._detailRoom = e.detail.roomSlug;
    this._detailOpen = true;
  }

  private _handleRoomDetailClose() {
    this._detailOpen = false;
    this._detailRoom = '';
  }

  private _getGridClasses(): string {
    const classes = ['sc-room-grid'];

    if (this._config.compact) {
      classes.push('compact');
    }

    if (this._config.columns) {
      classes.push(`cols-${Math.min(3, Math.max(1, this._config.columns))}`);
    }

    return classes.join(' ');
  }

  render() {
    if (!this.hass) {
      return html`
        <ha-card>
          <div class="sc-card">
            <div class="sc-loading">
              <div class="sc-loading-dot"></div>
              <div class="sc-loading-dot"></div>
              <div class="sc-loading-dot"></div>
            </div>
          </div>
        </ha-card>
      `;
    }

    const showSchedule = this._config.show_schedule !== false;
    const showSuggestions = this._config.show_suggestions !== false;
    const compact = this._config.compact || false;

    return html`
      <ha-card>
        <div class="sc-card">
          <!-- 1. House Overview Header -->
          <house-overview .hass=${this.hass}></house-overview>

          <!-- 2. Room Grid -->
          ${this._rooms.length > 0
            ? html`
                <div class="sc-rooms-label">
                  Rooms (${this._rooms.length})
                </div>
                <div
                  class="${this._getGridClasses()}"
                  @room-detail-open=${this._handleRoomDetailOpen}
                >
                  ${this._rooms.map(
                    (room, idx) => html`
                      <room-tile
                        .hass=${this.hass}
                        .roomSlug=${room}
                        ?compact=${compact}
                        class="sc-fade-in"
                        style="animation-delay: ${idx * 50}ms"
                      ></room-tile>
                    `,
                  )}
                </div>
              `
            : html`
                <div class="sc-empty">
                  No Smart Climate rooms found. Make sure the Smart Climate
                  integration is configured.
                </div>
              `}

          <!-- 3. Schedule Timeline (collapsible) -->
          ${showSchedule
            ? html`<schedule-view .hass=${this.hass}></schedule-view>`
            : nothing}

          <!-- 4. AI Suggestions (collapsible) -->
          ${showSuggestions
            ? html`<suggestion-panel .hass=${this.hass}></suggestion-panel>`
            : nothing}
        </div>
      </ha-card>

      <!-- Room Detail Drawer (overlay) -->
      <room-detail
        .hass=${this.hass}
        .roomSlug=${this._detailRoom}
        ?open=${this._detailOpen}
        @room-detail-close=${this._handleRoomDetailClose}
      ></room-detail>
    `;
  }
}

// Register card with Home Assistant's custom card registry
(window as any).customCards = (window as any).customCards || [];
(window as any).customCards.push({
  type: 'smart-climate-card',
  name: 'Smart Climate Card',
  description:
    'A comprehensive dashboard card for the Smart Climate HA integration. Shows room comfort, HVAC status, schedules, and AI suggestions.',
  preview: true,
  documentationURL:
    'https://github.com/joshuaseidel/hass-climate-controll/tree/main/smart-climate-card',
});

declare global {
  interface HTMLElementTagNameMap {
    'smart-climate-card': SmartClimateCard;
  }
}
