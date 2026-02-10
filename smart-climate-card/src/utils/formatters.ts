/**
 * Formatting utilities for the Smart Climate card.
 */

/**
 * Format a temperature value with its unit.
 */
export function formatTemp(value: number | string | undefined, unit: string = '°F'): string {
  if (value === undefined || value === null || value === 'unknown' || value === 'unavailable') {
    return '--' + unit;
  }
  const num = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(num)) return '--' + unit;
  return `${Math.round(num * 10) / 10}${unit}`;
}

/**
 * Format a Date to a time string (HH:MM AM/PM).
 */
export function formatTime(date: Date): string {
  return date.toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  });
}

/**
 * Format a score value (0-100) as a display string.
 */
export function formatScore(score: number | string | undefined): string {
  if (score === undefined || score === null || score === 'unknown' || score === 'unavailable') {
    return '--';
  }
  const num = typeof score === 'string' ? parseFloat(score) : score;
  if (isNaN(num)) return '--';
  return `${Math.round(num)}`;
}

/**
 * Get the comfort color for a score (0-100).
 * 90+  -> green
 * 70+  -> blue
 * 50+  -> amber
 * 30+  -> orange
 * 0+   -> red
 */
export function getComfortColor(score: number | string | undefined): string {
  if (score === undefined || score === null || score === 'unknown' || score === 'unavailable') {
    return 'var(--sc-comfort-unknown, #9e9e9e)';
  }
  const num = typeof score === 'string' ? parseFloat(score) : score;
  if (isNaN(num)) return 'var(--sc-comfort-unknown, #9e9e9e)';

  if (num >= 90) return 'var(--sc-comfort-excellent, #4caf50)';
  if (num >= 70) return 'var(--sc-comfort-good, #2196f3)';
  if (num >= 50) return 'var(--sc-comfort-fair, #ffc107)';
  if (num >= 30) return 'var(--sc-comfort-poor, #ff9800)';
  return 'var(--sc-comfort-bad, #f44336)';
}

/**
 * Get a human-readable label for a comfort score.
 */
export function getComfortLabel(score: number | string | undefined): string {
  if (score === undefined || score === null || score === 'unknown' || score === 'unavailable') {
    return 'Unknown';
  }
  const num = typeof score === 'string' ? parseFloat(score) : score;
  if (isNaN(num)) return 'Unknown';

  if (num >= 90) return 'Excellent';
  if (num >= 70) return 'Good';
  if (num >= 50) return 'Fair';
  if (num >= 30) return 'Poor';
  return 'Bad';
}

/**
 * Get a trend arrow character for a numeric trend value.
 * Positive = rising, negative = falling, near-zero = stable.
 */
export function getTrendArrow(trend: number | string | undefined): string {
  if (trend === undefined || trend === null || trend === 'unknown' || trend === 'unavailable') {
    return '';
  }
  const num = typeof trend === 'string' ? parseFloat(trend) : trend;
  if (isNaN(num)) return '';

  if (num > 0.5) return '↑';
  if (num > 0.1) return '↗';
  if (num < -0.5) return '↓';
  if (num < -0.1) return '↘';
  return '→';
}

/**
 * Get an icon/emoji for an HVAC action.
 */
export function getHvacIcon(action: string | undefined): string {
  if (!action) return '';
  switch (action.toLowerCase()) {
    case 'heating':
      return '🔥';
    case 'cooling':
      return '❄️';
    case 'idle':
      return '⏸';
    case 'fan':
      return '🌀';
    case 'drying':
      return '💧';
    case 'off':
      return '⏻';
    default:
      return '';
  }
}

/**
 * Get the HVAC action color.
 */
export function getHvacColor(action: string | undefined): string {
  if (!action) return 'var(--sc-hvac-idle, #9e9e9e)';
  switch (action.toLowerCase()) {
    case 'heating':
      return 'var(--sc-hvac-heating, #ff5722)';
    case 'cooling':
      return 'var(--sc-hvac-cooling, #2196f3)';
    case 'fan':
      return 'var(--sc-hvac-fan, #00bcd4)';
    case 'drying':
      return 'var(--sc-hvac-drying, #ff9800)';
    case 'idle':
    case 'off':
    default:
      return 'var(--sc-hvac-idle, #9e9e9e)';
  }
}

/**
 * Format a duration in minutes to a readable string.
 */
export function formatDuration(minutes: number | string | undefined): string {
  if (minutes === undefined || minutes === null || minutes === 'unknown' || minutes === 'unavailable') {
    return '--';
  }
  const num = typeof minutes === 'string' ? parseFloat(minutes) : minutes;
  if (isNaN(num)) return '--';

  if (num < 60) return `${Math.round(num)}m`;
  const hours = Math.floor(num / 60);
  const mins = Math.round(num % 60);
  return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
}

/**
 * Generate confidence dots for a 0-5 rating.
 */
export function confidenceDots(level: number): string {
  const filled = Math.min(Math.max(Math.round(level), 0), 5);
  const empty = 5 - filled;
  return '●'.repeat(filled) + '○'.repeat(empty);
}
