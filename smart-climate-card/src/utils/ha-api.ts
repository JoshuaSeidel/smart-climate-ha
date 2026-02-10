/**
 * Home Assistant WebSocket API helpers for the Smart Climate card.
 */

export interface HomeAssistant {
  states: Record<string, HassEntity>;
  callService(domain: string, service: string, data?: Record<string, any>): Promise<void>;
  callWS(msg: Record<string, any>): Promise<any>;
  connection: any;
}

export interface HassEntity {
  entity_id: string;
  state: string;
  attributes: Record<string, any>;
  last_changed: string;
  last_updated: string;
}

/**
 * Call a Home Assistant service.
 */
export function callService(
  hass: HomeAssistant,
  domain: string,
  service: string,
  data: Record<string, any> = {},
): Promise<void> {
  return hass.callService(domain, service, data);
}

/**
 * Get the state object for an entity, or undefined if it doesn't exist.
 */
export function getEntityState(
  hass: HomeAssistant,
  entityId: string,
): HassEntity | undefined {
  if (!hass || !hass.states) return undefined;
  return hass.states[entityId];
}

/**
 * Subscribe to entity state changes via the HA connection.
 * Returns an unsubscribe function.
 */
export function subscribeEntities(
  hass: HomeAssistant,
  callback: (states: Record<string, HassEntity>) => void,
): () => void {
  if (!hass || !hass.connection) {
    return () => {};
  }

  let unsub: (() => void) | null = null;

  hass.connection
    .subscribeEvents((event: any) => {
      if (event.event_type === 'state_changed') {
        callback(hass.states);
      }
    }, 'state_changed')
    .then((unsubFn: () => void) => {
      unsub = unsubFn;
    });

  return () => {
    if (unsub) unsub();
  };
}

/**
 * Discover all rooms managed by Smart Climate by finding entities
 * matching the pattern sensor.sc_*_comfort_score.
 */
export function discoverRooms(hass: HomeAssistant): string[] {
  if (!hass || !hass.states) return [];

  const rooms: string[] = [];
  const pattern = /^sensor\.sc_(.+)_comfort_score$/;

  for (const entityId of Object.keys(hass.states)) {
    const match = entityId.match(pattern);
    if (match && match[1] && match[1] !== 'house') {
      rooms.push(match[1]);
    }
  }

  return rooms.sort();
}

/**
 * Get the friendly name for a room slug.
 */
export function getRoomName(roomSlug: string): string {
  return roomSlug
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}
