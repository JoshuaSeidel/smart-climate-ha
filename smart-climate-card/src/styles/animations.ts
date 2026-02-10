import { css } from 'lit';

/**
 * Animation styles for the Smart Climate card.
 */
export const animationStyles = css`
  /* Heating pulse - warm glow */
  @keyframes sc-pulse-heating {
    0%, 100% {
      box-shadow: 0 0 4px rgba(255, 87, 34, 0.3);
    }
    50% {
      box-shadow: 0 0 12px rgba(255, 87, 34, 0.6);
    }
  }

  .sc-pulse-heating {
    animation: sc-pulse-heating 2s ease-in-out infinite;
  }

  /* Cooling pulse - cool glow */
  @keyframes sc-pulse-cooling {
    0%, 100% {
      box-shadow: 0 0 4px rgba(33, 150, 243, 0.3);
    }
    50% {
      box-shadow: 0 0 12px rgba(33, 150, 243, 0.6);
    }
  }

  .sc-pulse-cooling {
    animation: sc-pulse-cooling 2s ease-in-out infinite;
  }

  /* HVAC action dot pulse */
  @keyframes sc-dot-pulse {
    0%, 100% {
      opacity: 1;
      transform: scale(1);
    }
    50% {
      opacity: 0.6;
      transform: scale(1.3);
    }
  }

  .sc-dot-pulse {
    animation: sc-dot-pulse 1.5s ease-in-out infinite;
  }

  /* Smooth value transition */
  .sc-value-transition {
    transition: color 0.3s ease, transform 0.2s ease;
  }

  /* Collapse/expand transition */
  .sc-collapse {
    overflow: hidden;
    max-height: 0;
    opacity: 0;
    transition: max-height 0.4s cubic-bezier(0.4, 0, 0.2, 1),
                opacity 0.3s ease;
  }

  .sc-collapse.expanded {
    max-height: 2000px;
    opacity: 1;
  }

  /* Fade in animation for tiles */
  @keyframes sc-fade-in {
    from {
      opacity: 0;
      transform: translateY(8px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .sc-fade-in {
    animation: sc-fade-in 0.3s ease forwards;
  }

  /* Slide up for drawer/modal */
  @keyframes sc-slide-up {
    from {
      opacity: 0;
      transform: translateY(100%);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .sc-slide-up {
    animation: sc-slide-up 0.35s cubic-bezier(0.4, 0, 0.2, 1) forwards;
  }

  /* Spin animation for fan */
  @keyframes sc-spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }

  .sc-spin {
    animation: sc-spin 2s linear infinite;
  }

  /* Shimmer loading effect */
  @keyframes sc-shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
  }

  .sc-shimmer {
    background: linear-gradient(
      90deg,
      rgba(255, 255, 255, 0.03) 25%,
      rgba(255, 255, 255, 0.08) 50%,
      rgba(255, 255, 255, 0.03) 75%
    );
    background-size: 200% 100%;
    animation: sc-shimmer 1.5s ease-in-out infinite;
  }

  /* Glow effect for occupied rooms */
  @keyframes sc-glow {
    0%, 100% {
      box-shadow: 0 0 8px rgba(255, 193, 7, 0.2);
    }
    50% {
      box-shadow: 0 0 16px rgba(255, 193, 7, 0.4);
    }
  }

  .sc-glow-occupied {
    animation: sc-glow 3s ease-in-out infinite;
  }

  /* Scale button press */
  .sc-press {
    transition: transform 0.1s ease;
  }

  .sc-press:active {
    transform: scale(0.95);
  }
`;
