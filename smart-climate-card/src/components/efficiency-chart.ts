import { LitElement, html, css, nothing, svg } from 'lit';
import { customElement, property } from 'lit/decorators.js';
import { themeStyles } from '../styles/theme';
import type { HomeAssistant } from '../utils/ha-api';
import { getEntityState } from '../utils/ha-api';
import { getComfortColor } from '../utils/formatters';

/**
 * <efficiency-chart> component
 * SVG mini bar chart showing efficiency data for a room or the whole house.
 */
@customElement('efficiency-chart')
export class EfficiencyChart extends LitElement {
  @property({ attribute: false }) hass!: HomeAssistant;
  @property({ type: String }) roomSlug: string = '';

  static styles = [
    themeStyles,
    css`
      :host {
        display: block;
      }

      .chart-container {
        padding: var(--sc-space-sm) 0;
      }

      .chart-label {
        font-size: var(--sc-font-xs);
        color: var(--sc-text-muted);
        margin-bottom: var(--sc-space-xs);
        text-transform: uppercase;
        letter-spacing: 0.5px;
      }

      svg {
        width: 100%;
        height: 48px;
        display: block;
      }

      .chart-legend {
        display: flex;
        justify-content: space-between;
        font-size: var(--sc-font-xs);
        color: var(--sc-text-muted);
        margin-top: 2px;
      }
    `,
  ];

  private _getEfficiencyData(): number[] {
    const entity = getEntityState(
      this.hass,
      this.roomSlug
        ? `sensor.sc_${this.roomSlug}_efficiency`
        : 'sensor.sc_house_efficiency',
    );

    if (!entity) return [];

    // Try to get historical data from attributes
    const history: number[] = entity.attributes?.hourly_data || [];

    if (history.length > 0) {
      return history.slice(-12); // Last 12 data points
    }

    // Fallback: just the current value as a single bar
    const val = parseFloat(entity.state);
    if (!isNaN(val)) {
      return [val];
    }

    return [];
  }

  private _renderBars(data: number[]) {
    if (data.length === 0) return nothing;

    const maxBars = 12;
    const chartWidth = 100; // percentage-based
    const chartHeight = 40;
    const barGap = 2;
    const barWidth = (chartWidth - barGap * (maxBars - 1)) / maxBars;

    const bars = data.map((value, index) => {
      const barHeight = Math.max(2, (value / 100) * chartHeight);
      const x = index * (barWidth + barGap);
      const y = chartHeight - barHeight;
      const color = getComfortColor(value);

      return svg`
        <rect
          x="${x}%"
          y="${y}"
          width="${barWidth}%"
          height="${barHeight}"
          rx="2"
          ry="2"
          fill="${color}"
          opacity="0.8"
        >
          <title>${Math.round(value)}%</title>
        </rect>
      `;
    });

    return svg`
      <svg viewBox="0 0 100 ${chartHeight}" preserveAspectRatio="none">
        <!-- Grid lines -->
        <line x1="0" y1="${chartHeight * 0.25}" x2="100" y2="${chartHeight * 0.25}"
              stroke="rgba(255,255,255,0.05)" stroke-width="0.5" />
        <line x1="0" y1="${chartHeight * 0.5}" x2="100" y2="${chartHeight * 0.5}"
              stroke="rgba(255,255,255,0.05)" stroke-width="0.5" />
        <line x1="0" y1="${chartHeight * 0.75}" x2="100" y2="${chartHeight * 0.75}"
              stroke="rgba(255,255,255,0.05)" stroke-width="0.5" />
        ${bars}
      </svg>
    `;
  }

  render() {
    const data = this._getEfficiencyData();

    if (data.length === 0) return nothing;

    return html`
      <div class="chart-container">
        <div class="chart-label">Efficiency</div>
        ${this._renderBars(data)}
        <div class="chart-legend">
          <span>${data.length > 1 ? `-${data.length}h` : 'Now'}</span>
          <span>Now</span>
        </div>
      </div>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'efficiency-chart': EfficiencyChart;
  }
}
