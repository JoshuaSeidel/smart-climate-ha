"""DataUpdateCoordinator for the Smart Climate integration."""

from __future__ import annotations

import contextlib
import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import CALLBACK_TYPE, HomeAssistant
from homeassistant.helpers.event import async_track_time_change
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    AI_PROVIDER_NONE,
    COMFORT_POOR,
    CONF_AI_ANALYSIS_TIME,
    CONF_AI_PROVIDER,
    CONF_AUXILIARY_DELAY_MINUTES,
    CONF_AUXILIARY_MAX_RUNTIME,
    CONF_AUXILIARY_THRESHOLD,
    CONF_AWAY_TEMP_OFFSET,
    CONF_COMFORT_HUMIDITY_WEIGHT,
    CONF_COMFORT_TEMP_WEIGHT,
    CONF_ENABLE_FOLLOW_ME,
    CONF_ENABLE_ZONE_BALANCING,
    CONF_FOLLOW_ME_COOLDOWN,
    CONF_OPERATION_MODE,
    CONF_OUTDOOR_TEMP_SENSOR,
    CONF_ROOMS,
    CONF_SCHEDULES,
    CONF_UPDATE_INTERVAL,
    CONF_WEATHER_ENTITY,
    DEFAULT_AI_ANALYSIS_TIME,
    DEFAULT_AUXILIARY_DELAY_MINUTES,
    DEFAULT_AUXILIARY_MAX_RUNTIME,
    DEFAULT_AUXILIARY_THRESHOLD,
    DEFAULT_AWAY_TEMP_OFFSET,
    DEFAULT_COMFORT_HUMIDITY_WEIGHT,
    DEFAULT_COMFORT_TEMP_WEIGHT,
    DEFAULT_ENABLE_FOLLOW_ME,
    DEFAULT_ENABLE_ZONE_BALANCING,
    DEFAULT_FOLLOW_ME_COOLDOWN,
    DEFAULT_OPERATION_MODE,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
    EVENT_AUXILIARY_ACTIVATED,
    EVENT_AUXILIARY_DEACTIVATED,
    EVENT_COMFORT_ALERT,
    EVENT_FOLLOW_ME_CHANGED,
    EVENT_SCHEDULE_ACTIVATED,
    EVENT_SCHEDULE_DEACTIVATED,
    EVENT_WINDOW_OPEN_ADJUSTED,
    OPERATION_MODE_ACTIVE,
    OPERATION_MODE_DISABLED,
    SUGGESTION_PENDING,
)
from .helpers.auxiliary import (
    async_disengage_auxiliary,
    async_engage_auxiliary,
    should_disengage_auxiliary,
    should_engage_auxiliary,
)
from .helpers.comfort import calculate_comfort_score
from .helpers.efficiency import (
    calculate_cooling_degree_days,
    calculate_efficiency_score,
    calculate_heating_degree_days,
)
from .helpers.presence import calculate_follow_me_targets, determine_follow_me_target
from .helpers.scheduling import get_house_active_schedule, get_winning_schedule
from .helpers.vents import async_apply_vent_positions, calculate_vent_positions
from .models import (
    AuxiliaryDeviceState,
    AuxiliaryDeviceType,
    HouseState,
    HVACAction,
    RoomConfig,
    RoomState,
    Schedule,
)

_LOGGER = logging.getLogger(__name__)

# Number of recent temperature readings to keep for trend calculation
TEMP_HISTORY_SIZE = 5


class SmartClimateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator that polls entity states, computes room/house state each cycle.

    Stored data shape:
        {
            "rooms": {slug: RoomState, ...},
            "house": HouseState,
        }
    """

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.entry = entry
        self._scheduled_tasks: list[CALLBACK_TYPE] = []

        # Parse room configs
        self.room_configs: dict[str, RoomConfig] = {}
        for room_data in entry.data.get(CONF_ROOMS, []):
            cfg = RoomConfig.from_dict(room_data)
            self.room_configs[cfg.slug] = cfg

        # Parse schedule configs
        self.schedules: list[Schedule] = []
        for sched_data in entry.data.get(CONF_SCHEDULES, []):
            self.schedules.append(Schedule.from_dict(sched_data))

        # Auxiliary device tracking: room_slug -> entity_id -> AuxiliaryDeviceState
        self._auxiliary_states: dict[str, dict[str, AuxiliaryDeviceState]] = {}
        for slug, cfg in self.room_configs.items():
            self._auxiliary_states[slug] = {}
            for entity_id in cfg.auxiliary_entities:
                domain = entity_id.split(".")[0]
                try:
                    device_type = AuxiliaryDeviceType(domain)
                except ValueError:
                    device_type = AuxiliaryDeviceType.SWITCH
                self._auxiliary_states[slug][entity_id] = AuxiliaryDeviceState(
                    entity_id=entity_id,
                    device_type=device_type,
                    max_runtime=entry.data.get(
                        CONF_AUXILIARY_MAX_RUNTIME, DEFAULT_AUXILIARY_MAX_RUNTIME
                    ),
                    threshold=entry.data.get(
                        CONF_AUXILIARY_THRESHOLD, DEFAULT_AUXILIARY_THRESHOLD
                    ),
                    delay_minutes=entry.data.get(
                        CONF_AUXILIARY_DELAY_MINUTES, DEFAULT_AUXILIARY_DELAY_MINUTES
                    ),
                )

        # Persistent room state across updates (keyed by slug)
        self._room_states: dict[str, RoomState] = {}
        for slug, cfg in self.room_configs.items():
            self._room_states[slug] = RoomState(config=cfg)

        # House-level state
        self._house_state = HouseState()

        # Previous follow-me target (for change detection / events)
        self._prev_follow_me_target: str | None = None

        # Operation mode: "active" (full control), "training" (observe only),
        # "disabled" (paused). Can be changed at runtime via the select entity.
        self.operation_mode: str = entry.data.get(
            CONF_OPERATION_MODE, DEFAULT_OPERATION_MODE
        )

        interval = entry.data.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=interval),
        )

    # ------------------------------------------------------------------
    # Main update loop
    # ------------------------------------------------------------------

    async def _async_update_data(self) -> dict[str, Any]:
        """Poll all tracked entities and recompute state."""
        now = datetime.now()

        # If disabled, skip all processing
        if self.operation_mode == OPERATION_MODE_DISABLED:
            return {"rooms": self._room_states, "house": self._house_state}

        # ---- per-room updates (always run: data collection) ----------
        for slug, room_cfg in self.room_configs.items():
            try:
                self._update_room(slug, room_cfg, now)
            except Exception:
                _LOGGER.exception(
                    "Error updating room '%s'; skipping this cycle", slug
                )

        rooms = self._room_states

        # In training mode, we collect data and compute scores but
        # do NOT apply follow-me, zone balancing, auxiliary, or vent changes.
        is_active = self.operation_mode == OPERATION_MODE_ACTIVE

        # ---- follow-me logic (active mode only) ----------------------
        enable_follow_me = self.entry.data.get(
            CONF_ENABLE_FOLLOW_ME, DEFAULT_ENABLE_FOLLOW_ME
        )
        if is_active and enable_follow_me:
            try:
                self._run_follow_me(rooms, now)
            except Exception:
                _LOGGER.exception("Error running follow-me logic")

        # ---- schedule engine (active mode only) ----------------------
        if is_active:
            try:
                self._run_schedules(rooms, now)
            except Exception:
                _LOGGER.exception("Error running schedule engine")

        # ---- zone balancing / vents (active mode only) ---------------
        enable_zone_balancing = self.entry.data.get(
            CONF_ENABLE_ZONE_BALANCING, DEFAULT_ENABLE_ZONE_BALANCING
        )
        if is_active and enable_zone_balancing:
            try:
                await self._run_zone_balancing(rooms)
            except Exception:
                _LOGGER.exception("Error running zone balancing")

        # ---- auxiliary devices (active mode only) --------------------
        if is_active:
            try:
                await self._run_auxiliary_logic(rooms, now)
            except Exception:
                _LOGGER.exception("Error running auxiliary device logic")

        # ---- house-level aggregation ---------------------------------
        try:
            self._update_house_state(rooms, now)
        except Exception:
            _LOGGER.exception("Error updating house state")

        return {"rooms": rooms, "house": self._house_state}

    # ------------------------------------------------------------------
    # Room-level polling
    # ------------------------------------------------------------------

    def _update_room(
        self, slug: str, cfg: RoomConfig, now: datetime
    ) -> None:
        """Read entity states and refresh a single room's RoomState."""
        room = self._room_states[slug]

        # -- Temperature (average of configured sensors) ---------------
        temps: list[float] = []
        for entity_id in cfg.temp_sensors:
            value = self._get_numeric_state(entity_id)
            if value is not None:
                temps.append(value)
        if temps:
            room.temperature = round(sum(temps) / len(temps), 2)
        else:
            room.temperature = None

        # -- Humidity (average) ----------------------------------------
        humids: list[float] = []
        for entity_id in cfg.humidity_sensors:
            value = self._get_numeric_state(entity_id)
            if value is not None:
                humids.append(value)
        if humids:
            room.humidity = round(sum(humids) / len(humids), 2)
        else:
            room.humidity = None

        # -- Presence --------------------------------------------------
        room.occupied = any(
            self._get_binary_state(eid) for eid in cfg.presence_sensors
        )
        if room.occupied:
            room.last_presence_time = now

        # -- Door/window sensors (any open -> window_open) -------------
        prev_window_open = room.window_open
        room.window_open = any(
            self._get_binary_state(eid) for eid in cfg.door_window_sensors
        )
        if room.window_open and not prev_window_open:
            self.hass.bus.async_fire(
                EVENT_WINDOW_OPEN_ADJUSTED,
                {"room": slug, "room_name": cfg.name, "open": True},
            )

        # -- Climate entity --------------------------------------------
        climate_state = self.hass.states.get(cfg.climate_entity)
        if climate_state is not None:
            target = climate_state.attributes.get("temperature")
            if target is not None:
                with contextlib.suppress(ValueError, TypeError):
                    room.current_target = float(target)

            raw_action = climate_state.attributes.get("hvac_action", "idle")
            try:
                new_action = HVACAction(raw_action)
            except ValueError:
                new_action = HVACAction.IDLE

            # Track HVAC runtime and cycles
            self._track_hvac_runtime(room, new_action, now)
            room.hvac_action = new_action

        # -- Temperature trend (degrees per hour) ----------------------
        if room.temperature is not None:
            room.temp_history.append((now, room.temperature))
            # Keep only the last TEMP_HISTORY_SIZE readings
            if len(room.temp_history) > TEMP_HISTORY_SIZE:
                room.temp_history = room.temp_history[-TEMP_HISTORY_SIZE:]
            room.temp_trend = self._calculate_trend(room.temp_history)
        else:
            room.temp_trend = 0.0

        # -- Comfort score ---------------------------------------------
        temp_weight = self.entry.data.get(
            CONF_COMFORT_TEMP_WEIGHT, DEFAULT_COMFORT_TEMP_WEIGHT
        )
        humidity_weight = self.entry.data.get(
            CONF_COMFORT_HUMIDITY_WEIGHT, DEFAULT_COMFORT_HUMIDITY_WEIGHT
        )
        prev_comfort = room.comfort_score
        room.comfort_score = calculate_comfort_score(
            current_temp=room.temperature,
            target_temp=room.current_target,
            humidity=room.humidity,
            temp_weight=temp_weight,
            humidity_weight=humidity_weight,
        )

        # Fire comfort alert when score drops below threshold
        if prev_comfort >= COMFORT_POOR and room.comfort_score < COMFORT_POOR:
            self.hass.bus.async_fire(
                EVENT_COMFORT_ALERT,
                {
                    "room": slug,
                    "room_name": cfg.name,
                    "comfort_score": room.comfort_score,
                },
            )

        # -- Efficiency score ------------------------------------------
        outdoor_temp = self._get_outdoor_temperature()
        temp_deviation = (
            abs(room.temperature - room.current_target)
            if room.temperature is not None and room.current_target is not None
            else 0.0
        )
        room.efficiency_score = calculate_efficiency_score(
            hvac_runtime_minutes=room.hvac_runtime_today,
            hvac_cycles=room.hvac_cycles_today,
            temp_deviation=temp_deviation,
            outdoor_temp=outdoor_temp,
            target_temp=room.current_target,
            window_open=room.window_open,
        )

    # ------------------------------------------------------------------
    # HVAC runtime / cycle tracking
    # ------------------------------------------------------------------

    def _track_hvac_runtime(
        self, room: RoomState, new_action: HVACAction, now: datetime
    ) -> None:
        """Update runtime minutes and cycle count when hvac_action changes."""
        active_actions = {HVACAction.HEATING, HVACAction.COOLING}
        old_action = room.hvac_action

        if old_action != new_action:
            # Accumulate runtime for the period that just ended
            if old_action in active_actions and room.hvac_state_change_time is not None:
                elapsed = (now - room.hvac_state_change_time).total_seconds() / 60.0
                room.hvac_runtime_today += max(0.0, elapsed)

            # Detect a new cycle (transition from non-active to active)
            if new_action in active_actions and old_action not in active_actions:
                room.hvac_cycles_today += 1

            room.last_hvac_state = new_action.value
            room.hvac_state_change_time = now
        else:
            # Same action continues — accumulate runtime if active
            if new_action in active_actions and room.hvac_state_change_time is not None:
                elapsed = (now - room.hvac_state_change_time).total_seconds() / 60.0
                room.hvac_runtime_today += max(0.0, elapsed)
                room.hvac_state_change_time = now

    # ------------------------------------------------------------------
    # Temperature trend calculation
    # ------------------------------------------------------------------

    @staticmethod
    def _calculate_trend(
        history: list[tuple[datetime, float]],
    ) -> float:
        """Return temperature change in degrees per hour from recent readings.

        Uses a simple linear slope over the stored history window.
        """
        if len(history) < 2:
            return 0.0

        first_time, first_temp = history[0]
        last_time, last_temp = history[-1]
        elapsed_hours = (last_time - first_time).total_seconds() / 3600.0

        if elapsed_hours <= 0:
            return 0.0

        return round((last_temp - first_temp) / elapsed_hours, 2)

    # ------------------------------------------------------------------
    # Follow-me logic
    # ------------------------------------------------------------------

    def _run_follow_me(
        self, rooms: dict[str, RoomState], now: datetime
    ) -> None:
        """Determine the follow-me target room and adjust targets."""
        cooldown = self.entry.data.get(
            CONF_FOLLOW_ME_COOLDOWN, DEFAULT_FOLLOW_ME_COOLDOWN
        )
        away_offset = self.entry.data.get(
            CONF_AWAY_TEMP_OFFSET, DEFAULT_AWAY_TEMP_OFFSET
        )

        new_target = determine_follow_me_target(
            rooms,
            current_target=self._house_state.follow_me_target,
            cooldown_minutes=cooldown,
        )

        if new_target != self._prev_follow_me_target:
            self.hass.bus.async_fire(
                EVENT_FOLLOW_ME_CHANGED,
                {
                    "previous_room": self._prev_follow_me_target,
                    "new_room": new_target,
                },
            )
            self._prev_follow_me_target = new_target

        self._house_state.follow_me_target = new_target

        # Calculate per-room follow-me targets
        fm_targets = calculate_follow_me_targets(
            rooms, primary_room=new_target, away_temp_offset=away_offset
        )

        for slug, smart_target in fm_targets.items():
            room = rooms[slug]
            room.smart_target = smart_target
            room.follow_me_active = slug == new_target

    # ------------------------------------------------------------------
    # Schedule engine
    # ------------------------------------------------------------------

    def _run_schedules(
        self, rooms: dict[str, RoomState], now: datetime
    ) -> None:
        """Evaluate schedules for each room and update active_schedule."""
        for slug, room in rooms.items():
            winning = get_winning_schedule(self.schedules, slug, now)
            prev_schedule = room.active_schedule
            new_schedule_name = winning.name if winning else None

            if new_schedule_name != prev_schedule:
                if new_schedule_name is not None:
                    self.hass.bus.async_fire(
                        EVENT_SCHEDULE_ACTIVATED,
                        {
                            "room": slug,
                            "room_name": room.config.name,
                            "schedule": new_schedule_name,
                        },
                    )
                elif prev_schedule is not None:
                    self.hass.bus.async_fire(
                        EVENT_SCHEDULE_DEACTIVATED,
                        {
                            "room": slug,
                            "room_name": room.config.name,
                            "schedule": prev_schedule,
                        },
                    )

            room.active_schedule = new_schedule_name

            # Apply schedule target if present and no user override
            if winning and not room.user_override_active:
                room.smart_target = winning.target_temperature + room.config.target_temp_offset
                room.last_adjustment_reason = f"Schedule: {winning.name}"

        # House-level active schedule
        self._house_state.active_schedule = get_house_active_schedule(
            self.schedules, now
        )

    # ------------------------------------------------------------------
    # Zone balancing / vents
    # ------------------------------------------------------------------

    async def _run_zone_balancing(
        self, rooms: dict[str, RoomState]
    ) -> None:
        """Calculate and apply smart vent positions."""
        positions = calculate_vent_positions(rooms)
        if positions:
            await async_apply_vent_positions(self.hass, positions)

    # ------------------------------------------------------------------
    # Auxiliary device logic
    # ------------------------------------------------------------------

    async def _run_auxiliary_logic(
        self, rooms: dict[str, RoomState], now: datetime
    ) -> None:
        """Engage or disengage auxiliary heating/cooling devices per room."""
        threshold = self.entry.data.get(
            CONF_AUXILIARY_THRESHOLD, DEFAULT_AUXILIARY_THRESHOLD
        )
        delay = self.entry.data.get(
            CONF_AUXILIARY_DELAY_MINUTES, DEFAULT_AUXILIARY_DELAY_MINUTES
        )

        for slug, room in rooms.items():
            aux_states = self._auxiliary_states.get(slug, {})
            if not aux_states:
                continue

            target_temp = room.smart_target if room.smart_target is not None else room.current_target
            if target_temp is None:
                continue

            for entity_id, aux_state in aux_states.items():
                # Update runtime if device is on
                if aux_state.is_on and aux_state.started_at is not None:
                    aux_state.runtime_minutes = (
                        now - aux_state.started_at
                    ).total_seconds() / 60.0

                if aux_state.is_on:
                    # Check if we should disengage
                    if should_disengage_auxiliary(room, target_temp, aux_state):
                        await async_disengage_auxiliary(self.hass, entity_id)
                        aux_state.is_on = False
                        aux_state.started_at = None
                        room.auxiliary_active = False
                        if entity_id in room.auxiliary_devices_on:
                            room.auxiliary_devices_on.remove(entity_id)
                        room.auxiliary_runtime_minutes += aux_state.runtime_minutes
                        aux_state.runtime_minutes = 0.0
                        room.auxiliary_reason = ""
                        self.hass.bus.async_fire(
                            EVENT_AUXILIARY_DEACTIVATED,
                            {
                                "room": slug,
                                "room_name": room.config.name,
                                "entity_id": entity_id,
                                "runtime_minutes": round(
                                    room.auxiliary_runtime_minutes, 1
                                ),
                            },
                        )
                else:
                    # Check if we should engage
                    if should_engage_auxiliary(
                        room, target_temp, threshold=threshold, delay_minutes=delay
                    ):
                        temp_deviation = (
                            room.temperature - target_temp
                            if room.temperature is not None
                            else 0.0
                        )
                        await async_engage_auxiliary(
                            self.hass, entity_id, target_temp, temp_deviation
                        )
                        aux_state.is_on = True
                        aux_state.started_at = now
                        aux_state.runtime_minutes = 0.0
                        room.auxiliary_active = True
                        if entity_id not in room.auxiliary_devices_on:
                            room.auxiliary_devices_on.append(entity_id)
                        room.auxiliary_reason = (
                            f"HVAC struggling to reach {target_temp}"
                        )
                        self.hass.bus.async_fire(
                            EVENT_AUXILIARY_ACTIVATED,
                            {
                                "room": slug,
                                "room_name": room.config.name,
                                "entity_id": entity_id,
                                "target_temp": target_temp,
                            },
                        )

    # ------------------------------------------------------------------
    # House-level aggregation
    # ------------------------------------------------------------------

    def _update_house_state(
        self, rooms: dict[str, RoomState], now: datetime
    ) -> None:
        """Aggregate room data into HouseState."""
        house = self._house_state

        # Average comfort / efficiency across rooms with valid scores
        comfort_scores = [r.comfort_score for r in rooms.values() if r.comfort_score > 0]
        efficiency_scores = [r.efficiency_score for r in rooms.values() if r.efficiency_score > 0]

        house.comfort_score = (
            round(sum(comfort_scores) / len(comfort_scores), 1)
            if comfort_scores
            else 0.0
        )
        house.efficiency_score = (
            round(sum(efficiency_scores) / len(efficiency_scores), 1)
            if efficiency_scores
            else 0.0
        )

        # Total runtime
        house.total_hvac_runtime = round(
            sum(r.hvac_runtime_today for r in rooms.values()), 1
        )

        # Outdoor conditions
        outdoor_temp = self._get_outdoor_temperature()
        house.outdoor_temperature = outdoor_temp

        weather_entity_id = self.entry.data.get(CONF_WEATHER_ENTITY)
        if weather_entity_id:
            weather_state = self.hass.states.get(weather_entity_id)
            if weather_state is not None:
                raw_humidity = weather_state.attributes.get("humidity")
                if raw_humidity is not None:
                    with contextlib.suppress(ValueError, TypeError):
                        house.outdoor_humidity = float(raw_humidity)

        # Degree days
        if outdoor_temp is not None:
            house.heating_degree_days = calculate_heating_degree_days(outdoor_temp)
            house.cooling_degree_days = calculate_cooling_degree_days(outdoor_temp)

    # ------------------------------------------------------------------
    # Helper: read entity states
    # ------------------------------------------------------------------

    def _get_numeric_state(self, entity_id: str) -> float | None:
        """Return a float value for a sensor entity, or None if unavailable."""
        state = self.hass.states.get(entity_id)
        if state is None or state.state in ("unavailable", "unknown", ""):
            return None
        try:
            return float(state.state)
        except (ValueError, TypeError):
            return None

    def _get_binary_state(self, entity_id: str) -> bool:
        """Return True if a binary_sensor / input_boolean is 'on'."""
        state = self.hass.states.get(entity_id)
        if state is None:
            return False
        return state.state == "on"

    def _get_outdoor_temperature(self) -> float | None:
        """Return outdoor temperature from dedicated sensor or weather entity."""
        outdoor_sensor = self.entry.data.get(CONF_OUTDOOR_TEMP_SENSOR)
        if outdoor_sensor:
            value = self._get_numeric_state(outdoor_sensor)
            if value is not None:
                return value

        weather_entity_id = self.entry.data.get(CONF_WEATHER_ENTITY)
        if weather_entity_id:
            weather_state = self.hass.states.get(weather_entity_id)
            if weather_state is not None:
                raw = weather_state.attributes.get("temperature")
                if raw is not None:
                    try:
                        return float(raw)
                    except (ValueError, TypeError):
                        pass
        return None

    # ------------------------------------------------------------------
    # Daily AI analysis scheduling
    # ------------------------------------------------------------------

    def schedule_daily_analysis(self) -> None:
        """Schedule a daily AI analysis run using async_track_time_change."""
        analysis_time_str = self.entry.data.get(
            CONF_AI_ANALYSIS_TIME, DEFAULT_AI_ANALYSIS_TIME
        )
        try:
            parts = analysis_time_str.split(":")
            hour = int(parts[0])
            minute = int(parts[1])
        except (ValueError, IndexError):
            hour, minute = 6, 0

        unsub = async_track_time_change(
            self.hass,
            self._handle_daily_analysis,
            hour=hour,
            minute=minute,
            second=0,
        )
        self._scheduled_tasks.append(unsub)
        _LOGGER.debug(
            "Scheduled daily AI analysis at %02d:%02d", hour, minute
        )

    async def _handle_daily_analysis(self, _now: datetime) -> None:
        """Callback fired by async_track_time_change for daily analysis."""
        await self.async_trigger_analysis()

    # ------------------------------------------------------------------
    # Cancel scheduled tasks (called on unload)
    # ------------------------------------------------------------------

    def cancel_scheduled_tasks(self) -> None:
        """Cancel all scheduled callbacks (listeners, timers)."""
        for unsub in self._scheduled_tasks:
            unsub()
        self._scheduled_tasks.clear()
        _LOGGER.debug("Cancelled all scheduled Smart Climate tasks")

    # ------------------------------------------------------------------
    # AI analysis trigger
    # ------------------------------------------------------------------

    async def async_trigger_analysis(self) -> None:
        """Invoke the AI analysis pipeline.

        This is called on the daily schedule and can also be invoked manually
        through the ``trigger_analysis`` service.
        """
        provider = self.entry.data.get(CONF_AI_PROVIDER, AI_PROVIDER_NONE)
        if provider == AI_PROVIDER_NONE:
            _LOGGER.debug("AI provider is 'none'; skipping analysis")
            return

        _LOGGER.info("Triggering AI analysis with provider '%s'", provider)

        try:
            from .ai import async_run_analysis
        except ImportError:
            _LOGGER.warning("AI module not available; skipping analysis")
            return

        try:
            await async_run_analysis(hass=self.hass, coordinator=self)

            self._house_state.last_analysis_time = datetime.now(tz=timezone.utc)

            self.hass.bus.async_fire(
                f"{DOMAIN}_analysis_complete",
                {
                    "provider": provider,
                    "suggestion_count": len(
                        [s for s in self._house_state.suggestions if s.status == SUGGESTION_PENDING]
                    ),
                },
            )

            self._send_notification(
                "Smart Climate AI Analysis",
                self._format_analysis_notification(provider),
            )
        except Exception as err:
            _LOGGER.exception("AI analysis failed")
            self._send_notification(
                "Smart Climate AI Analysis Failed",
                f"Analysis with provider **{provider}** failed:\n\n`{err}`",
            )

    def _send_notification(self, title: str, message: str) -> None:
        """Create a persistent notification via the service bus."""
        self.hass.async_create_task(
            self.hass.services.async_call(
                "persistent_notification",
                "create",
                {
                    "title": title,
                    "message": message,
                    "notification_id": "smart_climate_analysis",
                },
            )
        )

    def _format_analysis_notification(self, provider: str) -> str:
        """Build markdown body for the analysis results notification."""
        house = self._house_state
        lines: list[str] = []

        if house.ai_daily_summary:
            lines.append("## Summary")
            lines.append(house.ai_daily_summary)
            lines.append("")

        pending = [s for s in house.suggestions if s.status == SUGGESTION_PENDING]
        if pending:
            lines.append(f"## Suggestions ({len(pending)} pending)")
            for s in pending:
                lines.append(f"### {s.title}")
                lines.append(f"**Priority:** {s.priority} | **Confidence:** {s.confidence:.0%}")
                if s.room:
                    lines.append(f"**Room:** {s.room}")
                if s.description:
                    lines.append(s.description)
                if s.reasoning:
                    lines.append(f"*Reasoning: {s.reasoning}*")
                lines.append("")

        lines.append("---")
        lines.append(
            f"*Provider: {provider} | "
            f"Analyzed: {house.last_analysis_time.strftime('%Y-%m-%d %H:%M') if house.last_analysis_time else 'N/A'}*"
        )

        return "\n".join(lines)
