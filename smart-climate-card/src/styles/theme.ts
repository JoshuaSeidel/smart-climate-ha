import { css } from 'lit';

/**
 * Theme CSS custom properties for the Smart Climate card.
 * These can be overridden by the user's HA theme.
 */
export const themeStyles = css`
  :host {
    /* Comfort score colors */
    --sc-comfort-excellent: #4caf50;
    --sc-comfort-good: #2196f3;
    --sc-comfort-fair: #ffc107;
    --sc-comfort-poor: #ff9800;
    --sc-comfort-bad: #f44336;
    --sc-comfort-unknown: #9e9e9e;

    /* HVAC action colors */
    --sc-hvac-heating: #ff5722;
    --sc-hvac-cooling: #2196f3;
    --sc-hvac-fan: #00bcd4;
    --sc-hvac-drying: #ff9800;
    --sc-hvac-idle: #9e9e9e;

    /* Card background - glassmorphism */
    --sc-card-bg: rgba(255, 255, 255, 0.08);
    --sc-card-bg-solid: rgba(32, 33, 36, 0.95);
    --sc-card-border: rgba(255, 255, 255, 0.12);
    --sc-card-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    --sc-backdrop-blur: blur(16px);

    /* Tile backgrounds */
    --sc-tile-bg: rgba(255, 255, 255, 0.05);
    --sc-tile-bg-hover: rgba(255, 255, 255, 0.1);
    --sc-tile-border: rgba(255, 255, 255, 0.08);
    --sc-tile-radius: 16px;

    /* Text colors */
    --sc-text-primary: rgba(255, 255, 255, 0.95);
    --sc-text-secondary: rgba(255, 255, 255, 0.6);
    --sc-text-muted: rgba(255, 255, 255, 0.35);

    /* Font sizes */
    --sc-font-xs: 0.65rem;
    --sc-font-sm: 0.75rem;
    --sc-font-md: 0.875rem;
    --sc-font-lg: 1.1rem;
    --sc-font-xl: 1.5rem;
    --sc-font-xxl: 2rem;

    /* Spacing */
    --sc-space-xs: 4px;
    --sc-space-sm: 8px;
    --sc-space-md: 12px;
    --sc-space-lg: 16px;
    --sc-space-xl: 24px;

    /* Border radius */
    --sc-radius-sm: 8px;
    --sc-radius-md: 12px;
    --sc-radius-lg: 16px;
    --sc-radius-xl: 24px;

    /* Occupied / follow-me glow */
    --sc-glow-occupied: 0 0 12px rgba(255, 193, 7, 0.4);
    --sc-glow-followme: 0 0 16px rgba(33, 150, 243, 0.5);

    /* Priority badge colors */
    --sc-priority-high: #f44336;
    --sc-priority-medium: #ff9800;
    --sc-priority-low: #4caf50;

    /* Section header */
    --sc-section-border: rgba(255, 255, 255, 0.06);
  }

  /* Light mode overrides - triggered by HA theme */
  :host([data-theme='light']) {
    --sc-card-bg: rgba(255, 255, 255, 0.75);
    --sc-card-bg-solid: rgba(248, 249, 250, 0.95);
    --sc-card-border: rgba(0, 0, 0, 0.08);
    --sc-card-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);

    --sc-tile-bg: rgba(255, 255, 255, 0.6);
    --sc-tile-bg-hover: rgba(255, 255, 255, 0.8);
    --sc-tile-border: rgba(0, 0, 0, 0.06);

    --sc-text-primary: rgba(0, 0, 0, 0.87);
    --sc-text-secondary: rgba(0, 0, 0, 0.54);
    --sc-text-muted: rgba(0, 0, 0, 0.3);

    --sc-section-border: rgba(0, 0, 0, 0.06);
  }
`;
