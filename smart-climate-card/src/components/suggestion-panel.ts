import { LitElement, html, css, nothing } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';
import { themeStyles } from '../styles/theme';
import { animationStyles } from '../styles/animations';
import { cardStyles } from '../styles/card-styles';
import type { HomeAssistant } from '../utils/ha-api';
import { getEntityState, callService } from '../utils/ha-api';
import { confidenceDots } from '../utils/formatters';

interface Suggestion {
  id: string;
  title: string;
  description: string;
  confidence: number;
  priority: string;
  category: string;
}

/**
 * <suggestion-panel> component
 * Collapsible panel showing AI suggestions with approve/reject buttons.
 */
@customElement('suggestion-panel')
export class SuggestionPanel extends LitElement {
  @property({ attribute: false }) hass!: HomeAssistant;
  @state() private _expanded: boolean = false;
  @state() private _loading: Set<string> = new Set();

  static styles = [
    themeStyles,
    animationStyles,
    cardStyles,
    css`
      :host {
        display: block;
      }

      .suggestion-list {
        display: flex;
        flex-direction: column;
        gap: var(--sc-space-sm);
        padding: var(--sc-space-sm) 0;
      }

      .suggestion-card {
        background: var(--sc-tile-bg);
        border: 1px solid var(--sc-tile-border);
        border-radius: var(--sc-radius-md);
        padding: var(--sc-space-md);
        transition: background 0.2s ease;
      }

      .suggestion-card:hover {
        background: var(--sc-tile-bg-hover);
      }

      .suggestion-card.loading {
        opacity: 0.5;
        pointer-events: none;
      }

      /* Card header */
      .suggestion-header {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: var(--sc-space-sm);
        margin-bottom: var(--sc-space-sm);
      }

      .suggestion-title {
        font-size: var(--sc-font-md);
        font-weight: 600;
        color: var(--sc-text-primary);
        flex: 1;
      }

      .suggestion-priority {
        font-size: var(--sc-font-xs);
        font-weight: 600;
        padding: 2px 8px;
        border-radius: var(--sc-radius-sm);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        flex-shrink: 0;
      }

      .suggestion-priority.high {
        background: rgba(244, 67, 54, 0.15);
        color: var(--sc-priority-high);
        border: 1px solid rgba(244, 67, 54, 0.3);
      }

      .suggestion-priority.medium {
        background: rgba(255, 152, 0, 0.15);
        color: var(--sc-priority-medium);
        border: 1px solid rgba(255, 152, 0, 0.3);
      }

      .suggestion-priority.low {
        background: rgba(76, 175, 80, 0.15);
        color: var(--sc-priority-low);
        border: 1px solid rgba(76, 175, 80, 0.3);
      }

      /* Description */
      .suggestion-desc {
        font-size: var(--sc-font-sm);
        color: var(--sc-text-secondary);
        line-height: 1.5;
        margin-bottom: var(--sc-space-sm);
      }

      /* Confidence row */
      .suggestion-meta {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: var(--sc-space-sm);
      }

      .suggestion-confidence {
        font-size: var(--sc-font-sm);
        color: var(--sc-text-muted);
        display: flex;
        align-items: center;
        gap: var(--sc-space-xs);
      }

      .confidence-dots {
        letter-spacing: 1px;
        color: var(--sc-comfort-fair);
      }

      .suggestion-category {
        font-size: var(--sc-font-xs);
        color: var(--sc-text-muted);
        background: rgba(255, 255, 255, 0.04);
        padding: 2px 6px;
        border-radius: 4px;
      }

      /* Action buttons */
      .suggestion-actions {
        display: flex;
        gap: var(--sc-space-sm);
        justify-content: flex-end;
      }

      /* Bulk actions */
      .bulk-actions {
        display: flex;
        justify-content: flex-end;
        gap: var(--sc-space-sm);
        padding-top: var(--sc-space-sm);
        border-top: 1px solid var(--sc-section-border);
        margin-top: var(--sc-space-sm);
      }

      /* Daily summary */
      .daily-summary {
        font-size: var(--sc-font-sm);
        color: var(--sc-text-secondary);
        line-height: 1.5;
        padding: var(--sc-space-sm);
        background: var(--sc-tile-bg);
        border-radius: var(--sc-radius-sm);
        margin-bottom: var(--sc-space-sm);
        border-left: 3px solid var(--sc-comfort-good);
      }

      .daily-summary-label {
        font-size: var(--sc-font-xs);
        color: var(--sc-text-muted);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: var(--sc-space-xs);
      }

      .last-analysis {
        font-size: var(--sc-font-xs);
        color: var(--sc-text-muted);
        text-align: right;
        margin-top: var(--sc-space-sm);
      }
    `,
  ];

  private _getSuggestionCount(): number {
    const entity = getEntityState(this.hass, 'sensor.sc_ai_suggestion_count');
    if (!entity) return 0;
    const num = parseInt(entity.state, 10);
    return isNaN(num) ? 0 : num;
  }

  private _getSuggestions(): Suggestion[] {
    const countEntity = getEntityState(
      this.hass,
      'sensor.sc_ai_suggestion_count',
    );
    if (!countEntity) return [];

    // Get suggestion list from the count sensor's attributes
    const pendingTitles: string[] =
      countEntity.attributes?.pending_titles || [];
    const pendingIds: string[] = countEntity.attributes?.pending_ids || [];

    // Try to get full details from the daily summary sensor attributes
    const summaryEntity = getEntityState(
      this.hass,
      'sensor.sc_ai_daily_summary',
    );
    const fullSuggestions: Suggestion[] =
      summaryEntity?.attributes?.suggestions || [];

    if (fullSuggestions.length > 0) {
      return fullSuggestions;
    }

    // Fallback: build minimal suggestions from count sensor attributes
    return pendingTitles.map((title, index) => ({
      id: pendingIds[index] || `suggestion_${index}`,
      title,
      description: '',
      confidence: 3,
      priority: 'medium',
      category: 'general',
    }));
  }

  private _getDailySummary(): string {
    const entity = getEntityState(this.hass, 'sensor.sc_ai_daily_summary');
    return entity?.state || '';
  }

  private _getLastAnalysis(): string {
    const entity = getEntityState(this.hass, 'sensor.sc_ai_last_analysis');
    if (!entity || entity.state === 'unknown' || entity.state === 'unavailable')
      return '';
    return entity.state;
  }

  private _toggleExpand() {
    this._expanded = !this._expanded;
  }

  private async _approve(suggestionId: string) {
    this._loading = new Set([...this._loading, suggestionId]);
    this.requestUpdate();
    try {
      await callService(this.hass, 'smart_climate', 'approve_suggestion', {
        suggestion_id: suggestionId,
      });
    } catch (err) {
      console.error('Failed to approve suggestion:', err);
    }
    this._loading.delete(suggestionId);
    this._loading = new Set(this._loading);
    this.requestUpdate();
  }

  private async _reject(suggestionId: string) {
    this._loading = new Set([...this._loading, suggestionId]);
    this.requestUpdate();
    try {
      await callService(this.hass, 'smart_climate', 'reject_suggestion', {
        suggestion_id: suggestionId,
      });
    } catch (err) {
      console.error('Failed to reject suggestion:', err);
    }
    this._loading.delete(suggestionId);
    this._loading = new Set(this._loading);
    this.requestUpdate();
  }

  private async _approveAll() {
    const suggestions = this._getSuggestions();
    for (const s of suggestions) {
      await this._approve(s.id);
    }
  }

  private async _rejectAll() {
    const suggestions = this._getSuggestions();
    for (const s of suggestions) {
      await this._reject(s.id);
    }
  }

  render() {
    const count = this._getSuggestionCount();
    const suggestions = this._getSuggestions();
    const dailySummary = this._getDailySummary();
    const lastAnalysis = this._getLastAnalysis();

    return html`
      <div class="sc-section">
        <!-- Collapsible header -->
        <div class="sc-section-header" @click=${this._toggleExpand}>
          <div class="sc-section-title">
            AI Suggestions
            ${count > 0
              ? html`<span class="sc-section-badge">${count}</span>`
              : nothing}
          </div>
          <span class="sc-section-chevron ${this._expanded ? 'open' : ''}"
            >&#9662;</span
          >
        </div>

        <!-- Collapsible content -->
        <div class="sc-section-content ${this._expanded ? 'open' : ''}">
          <!-- Daily summary -->
          ${dailySummary &&
          dailySummary !== 'unknown' &&
          dailySummary !== 'unavailable'
            ? html`
                <div class="daily-summary">
                  <div class="daily-summary-label">Daily Summary</div>
                  ${dailySummary}
                </div>
              `
            : nothing}

          <!-- Suggestion cards -->
          ${suggestions.length > 0
            ? html`
                <div class="suggestion-list">
                  ${suggestions.map(
                    (s) => html`
                      <div
                        class="suggestion-card sc-fade-in ${this._loading.has(
                          s.id,
                        )
                          ? 'loading'
                          : ''}"
                      >
                        <div class="suggestion-header">
                          <span class="suggestion-title">${s.title}</span>
                          <span
                            class="suggestion-priority ${s.priority.toLowerCase()}"
                            >${s.priority}</span
                          >
                        </div>

                        ${s.description
                          ? html`<div class="suggestion-desc">
                              ${s.description}
                            </div>`
                          : nothing}

                        <div class="suggestion-meta">
                          <span class="suggestion-confidence">
                            Confidence:
                            <span class="confidence-dots"
                              >${confidenceDots(s.confidence)}</span
                            >
                          </span>
                          ${s.category
                            ? html`<span class="suggestion-category"
                                >${s.category}</span
                              >`
                            : nothing}
                        </div>

                        <div class="suggestion-actions">
                          <button
                            class="sc-btn danger small"
                            @click=${(e: Event) => {
                              e.stopPropagation();
                              this._reject(s.id);
                            }}
                          >
                            Reject
                          </button>
                          <button
                            class="sc-btn success small"
                            @click=${(e: Event) => {
                              e.stopPropagation();
                              this._approve(s.id);
                            }}
                          >
                            Approve
                          </button>
                        </div>
                      </div>
                    `,
                  )}
                </div>

                <!-- Bulk actions -->
                ${suggestions.length > 1
                  ? html`
                      <div class="bulk-actions">
                        <button
                          class="sc-btn danger small"
                          @click=${this._rejectAll}
                        >
                          Reject All
                        </button>
                        <button
                          class="sc-btn success small"
                          @click=${this._approveAll}
                        >
                          Approve All
                        </button>
                      </div>
                    `
                  : nothing}
              `
            : html`
                <div class="sc-empty">No pending suggestions</div>
              `}

          <!-- Last analysis time -->
          ${lastAnalysis
            ? html`<div class="last-analysis">
                Last analysis: ${lastAnalysis}
              </div>`
            : nothing}
        </div>
      </div>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'suggestion-panel': SuggestionPanel;
  }
}
