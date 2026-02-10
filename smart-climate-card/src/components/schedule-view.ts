import { LitElement, html, css, svg, nothing } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';
import { themeStyles } from '../styles/theme';
import { animationStyles } from '../styles/animations';
import { cardStyles } from '../styles/card-styles';
import type { HomeAssistant } from '../utils/ha-api';
import { getEntityState } from '../utils/ha-api';
import { formatTime } from '../utils/formatters';

interface ScheduleBlock {
  name: string;
  start_hour: number;
  start_minute: number;
  end_hour: number;
  end_minute: number;
  color: string;
}

/**
 * <schedule-view> component
 * Horizontal SVG timeline showing today's schedule blocks with a NOW marker.
 */
@customElement('schedule-view')
export class ScheduleView extends LitElement {
  @property({ attribute: false }) hass!: HomeAssistant;
  @state() private _expanded: boolean = false;

  static styles = [
    themeStyles,
    animationStyles,
    cardStyles,
    css`
      :host {
        display: block;
      }

      .timeline-container {
        padding: var(--sc-space-sm) 0;
      }

      .timeline-svg {
        width: 100%;
        height: 60px;
        display: block;
      }

      .timeline-labels {
        display: flex;
        justify-content: space-between;
        font-size: var(--sc-font-xs);
        color: var(--sc-text-muted);
        margin-top: var(--sc-space-xs);
        padding: 0 2px;
      }

      .schedule-legend {
        display: flex;
        flex-wrap: wrap;
        gap: var(--sc-space-sm);
        margin-top: var(--sc-space-sm);
        padding: var(--sc-space-xs) 0;
      }

      .legend-item {
        display: flex;
        align-items: center;
        gap: 4px;
        font-size: var(--sc-font-xs);
        color: var(--sc-text-secondary);
      }

      .legend-dot {
        width: 8px;
        height: 8px;
        border-radius: 2px;
        flex-shrink: 0;
      }

      .active-schedule-info {
        font-size: var(--sc-font-sm);
        color: var(--sc-text-secondary);
        margin-bottom: var(--sc-space-sm);
      }

      .active-schedule-name {
        color: var(--sc-text-primary);
        font-weight: 600;
      }
    `,
  ];

  // Schedule colors palette
  private _colors = [
    '#4caf50',
    '#2196f3',
    '#ff9800',
    '#9c27b0',
    '#00bcd4',
    '#e91e63',
    '#8bc34a',
    '#ff5722',
  ];

  private _getScheduleBlocks(): ScheduleBlock[] {
    const entity = getEntityState(this.hass, 'sensor.sc_active_schedule');
    if (!entity) return [];

    const schedules: ScheduleBlock[] =
      entity.attributes?.today_blocks || [];

    // Assign colors if not present
    const nameColorMap = new Map<string, string>();
    let colorIdx = 0;

    return schedules.map((block) => {
      if (!block.color) {
        if (!nameColorMap.has(block.name)) {
          nameColorMap.set(
            block.name,
            this._colors[colorIdx % this._colors.length],
          );
          colorIdx++;
        }
        return { ...block, color: nameColorMap.get(block.name) || '#9e9e9e' };
      }
      return block;
    });
  }

  private _toggleExpand() {
    this._expanded = !this._expanded;
  }

  private _timeToPercent(hour: number, minute: number): number {
    return ((hour * 60 + minute) / (24 * 60)) * 100;
  }

  private _renderTimeline(blocks: ScheduleBlock[]) {
    const now = new Date();
    const nowPercent = this._timeToPercent(now.getHours(), now.getMinutes());

    const svgWidth = 100; // viewBox percentage
    const barY = 15;
    const barHeight = 20;
    const totalHeight = 55;

    return svg`
      <svg
        class="timeline-svg"
        viewBox="0 0 ${svgWidth} ${totalHeight}"
        preserveAspectRatio="none"
      >
        <!-- Background track -->
        <rect
          x="0" y="${barY}"
          width="${svgWidth}" height="${barHeight}"
          rx="4" ry="4"
          fill="rgba(255,255,255,0.04)"
        />

        <!-- Hour markers -->
        ${[6, 12, 18].map(
          (hour) => svg`
            <line
              x1="${this._timeToPercent(hour, 0)}" y1="${barY}"
              x2="${this._timeToPercent(hour, 0)}" y2="${barY + barHeight}"
              stroke="rgba(255,255,255,0.08)"
              stroke-width="0.3"
            />
            <text
              x="${this._timeToPercent(hour, 0)}"
              y="${barY + barHeight + 10}"
              text-anchor="middle"
              fill="rgba(255,255,255,0.3)"
              font-size="3.5"
              font-family="sans-serif"
            >
              ${hour === 12 ? '12p' : hour < 12 ? `${hour}a` : `${hour - 12}p`}
            </text>
          `,
        )}

        <!-- Schedule blocks -->
        ${blocks.map((block) => {
          const startPct = this._timeToPercent(
            block.start_hour,
            block.start_minute,
          );
          const endPct = this._timeToPercent(block.end_hour, block.end_minute);
          const width = Math.max(0.5, endPct - startPct);

          return svg`
            <rect
              x="${startPct}" y="${barY + 1}"
              width="${width}" height="${barHeight - 2}"
              rx="2" ry="2"
              fill="${block.color}"
              opacity="0.7"
            >
              <title>${block.name}: ${block.start_hour}:${String(block.start_minute).padStart(2, '0')} - ${block.end_hour}:${String(block.end_minute).padStart(2, '0')}</title>
            </rect>
          `;
        })}

        <!-- NOW marker -->
        <line
          x1="${nowPercent}" y1="${barY - 4}"
          x2="${nowPercent}" y2="${barY + barHeight + 4}"
          stroke="#ff5252"
          stroke-width="0.6"
        />
        <circle
          cx="${nowPercent}" cy="${barY - 4}"
          r="2"
          fill="#ff5252"
        />
        <text
          x="${nowPercent}"
          y="${barY - 7}"
          text-anchor="middle"
          fill="#ff5252"
          font-size="3"
          font-weight="bold"
          font-family="sans-serif"
        >
          NOW
        </text>
      </svg>
    `;
  }

  render() {
    const blocks = this._getScheduleBlocks();
    const activeEntity = getEntityState(this.hass, 'sensor.sc_active_schedule');
    const activeName = activeEntity?.state || 'None';
    const now = new Date();

    // Build unique legend entries
    const legendNames = new Map<string, string>();
    blocks.forEach((b) => legendNames.set(b.name, b.color));

    return html`
      <div class="sc-section">
        <!-- Collapsible header -->
        <div class="sc-section-header" @click=${this._toggleExpand}>
          <div class="sc-section-title">
            Schedule
            <span class="sc-section-badge">${activeName}</span>
          </div>
          <span class="sc-section-chevron ${this._expanded ? 'open' : ''}"
            >&#9662;</span
          >
        </div>

        <!-- Collapsible content -->
        <div class="sc-section-content ${this._expanded ? 'open' : ''}">
          <div class="active-schedule-info">
            Active:
            <span class="active-schedule-name">${activeName}</span>
            &middot; ${formatTime(now)}
          </div>

          ${blocks.length > 0
            ? html`
                <div class="timeline-container">
                  ${this._renderTimeline(blocks)}
                  <div class="timeline-labels">
                    <span>12 AM</span>
                    <span>6 AM</span>
                    <span>12 PM</span>
                    <span>6 PM</span>
                    <span>12 AM</span>
                  </div>
                </div>

                <!-- Legend -->
                <div class="schedule-legend">
                  ${[...legendNames.entries()].map(
                    ([name, color]) => html`
                      <div class="legend-item">
                        <span
                          class="legend-dot"
                          style="background: ${color}"
                        ></span>
                        ${name}
                      </div>
                    `,
                  )}
                </div>
              `
            : html`<div class="sc-empty">No schedules configured for today</div>`}
        </div>
      </div>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'schedule-view': ScheduleView;
  }
}
