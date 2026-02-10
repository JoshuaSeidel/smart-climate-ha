import { css } from 'lit';

/**
 * Main card layout styles for the Smart Climate card.
 */
export const cardStyles = css`
  :host {
    display: block;
    font-family: var(--ha-card-font-family, 'Roboto', 'Noto', sans-serif);
    color: var(--sc-text-primary);
  }

  /* Main card container - glassmorphism */
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

  /* Room grid layout - responsive columns */
  .sc-room-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--sc-space-md);
    padding: var(--sc-space-sm) 0;
  }

  @media (min-width: 800px) {
    .sc-room-grid {
      grid-template-columns: repeat(3, 1fr);
    }
  }

  @media (max-width: 500px) {
    .sc-room-grid {
      grid-template-columns: 1fr;
    }
  }

  /* Compact mode: smaller tiles */
  .sc-room-grid.compact {
    gap: var(--sc-space-sm);
  }

  /* Section headers */
  .sc-section {
    margin-top: var(--sc-space-lg);
    border-top: 1px solid var(--sc-section-border);
    padding-top: var(--sc-space-md);
  }

  .sc-section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    cursor: pointer;
    padding: var(--sc-space-sm) 0;
    user-select: none;
    -webkit-user-select: none;
  }

  .sc-section-header:hover {
    opacity: 0.8;
  }

  .sc-section-title {
    font-size: var(--sc-font-md);
    font-weight: 600;
    color: var(--sc-text-primary);
    display: flex;
    align-items: center;
    gap: var(--sc-space-sm);
  }

  .sc-section-badge {
    background: var(--sc-tile-bg);
    border-radius: var(--sc-radius-sm);
    padding: 2px 8px;
    font-size: var(--sc-font-xs);
    font-weight: 500;
    color: var(--sc-text-secondary);
  }

  .sc-section-chevron {
    font-size: var(--sc-font-md);
    color: var(--sc-text-muted);
    transition: transform 0.3s ease;
  }

  .sc-section-chevron.open {
    transform: rotate(180deg);
  }

  .sc-section-content {
    overflow: hidden;
    max-height: 0;
    opacity: 0;
    transition: max-height 0.4s ease, opacity 0.3s ease;
  }

  .sc-section-content.open {
    max-height: 2000px;
    opacity: 1;
  }

  /* Buttons */
  .sc-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: var(--sc-space-xs);
    padding: var(--sc-space-sm) var(--sc-space-md);
    border: 1px solid var(--sc-tile-border);
    border-radius: var(--sc-radius-sm);
    background: var(--sc-tile-bg);
    color: var(--sc-text-primary);
    font-size: var(--sc-font-sm);
    font-weight: 500;
    cursor: pointer;
    transition: background 0.2s ease, border-color 0.2s ease;
    user-select: none;
    -webkit-user-select: none;
    outline: none;
  }

  .sc-btn:hover {
    background: var(--sc-tile-bg-hover);
  }

  .sc-btn:active {
    transform: scale(0.97);
  }

  .sc-btn.primary {
    background: rgba(33, 150, 243, 0.2);
    border-color: rgba(33, 150, 243, 0.4);
    color: #64b5f6;
  }

  .sc-btn.primary:hover {
    background: rgba(33, 150, 243, 0.3);
  }

  .sc-btn.success {
    background: rgba(76, 175, 80, 0.2);
    border-color: rgba(76, 175, 80, 0.4);
    color: #81c784;
  }

  .sc-btn.success:hover {
    background: rgba(76, 175, 80, 0.3);
  }

  .sc-btn.danger {
    background: rgba(244, 67, 54, 0.2);
    border-color: rgba(244, 67, 54, 0.4);
    color: #e57373;
  }

  .sc-btn.danger:hover {
    background: rgba(244, 67, 54, 0.3);
  }

  .sc-btn.small {
    padding: var(--sc-space-xs) var(--sc-space-sm);
    font-size: var(--sc-font-xs);
  }

  /* Progress bar base */
  .sc-progress {
    width: 100%;
    height: 6px;
    background: rgba(255, 255, 255, 0.08);
    border-radius: 3px;
    overflow: hidden;
  }

  .sc-progress-fill {
    height: 100%;
    border-radius: 3px;
    transition: width 0.6s ease, background-color 0.3s ease;
  }

  /* No data / empty state */
  .sc-empty {
    text-align: center;
    padding: var(--sc-space-xl);
    color: var(--sc-text-muted);
    font-size: var(--sc-font-md);
  }

  /* Overlay / drawer backdrop */
  .sc-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.6);
    backdrop-filter: blur(4px);
    -webkit-backdrop-filter: blur(4px);
    z-index: 999;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  /* Loading dots */
  .sc-loading {
    display: flex;
    gap: var(--sc-space-xs);
    justify-content: center;
    padding: var(--sc-space-lg);
  }

  .sc-loading-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--sc-text-muted);
    animation: sc-loading-bounce 1.4s infinite ease-in-out both;
  }

  .sc-loading-dot:nth-child(1) { animation-delay: -0.32s; }
  .sc-loading-dot:nth-child(2) { animation-delay: -0.16s; }

  @keyframes sc-loading-bounce {
    0%, 80%, 100% { transform: scale(0); }
    40% { transform: scale(1); }
  }
`;
