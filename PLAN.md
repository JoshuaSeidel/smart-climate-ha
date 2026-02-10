# Smart Climate - AI-Powered Home Assistant Integration

## Context

Ecobee and similar smart thermostats can track presence and focus heating/cooling on occupied rooms, but this often unbalances temperatures across the house. This integration creates a **device-agnostic, AI-powered climate control system** for Home Assistant that works with ANY climate entity, combines multiple sensor types per room (temperature, humidity, presence, door/window), and uses LLMs to analyze trends, predict patterns, and generate daily actionable suggestions the user can approve before they're applied.

**Target**: Home Assistant 2026.2 SDK, HACS-ready custom integration + custom Lovelace card.

---

## Architecture Overview

```
  HA Climate/Sensor Entities (any brand)
              │
    ┌─────────▼──────────┐
    │ SmartClimateCoordinator │  ← polls every 60s
    │  (DataUpdateCoordinator) │
    │                          │
    │  • Room state aggregation│
    │  • Comfort scoring       │
    │  • Efficiency scoring    │
    │  • HVAC runtime tracking │
    │  • Follow-me logic       │
    │  • Zone balancing        │
    │  • Vent control          │
    └────┬──────────┬─────────┘
         │          │
   ┌─────▼────┐  ┌──▼──────────────┐
   │ Entities  │  │ AI Analysis      │
   │ (sensor,  │  │ Pipeline         │
   │  climate, │  │ (daily/on-demand)│
   │  binary)  │  │                  │
   └─────┬─────┘  │ Data → LLM →    │
         │        │ Suggestions →    │
   ┌─────▼─────┐  │ Approve → Act   │
   │ Custom    │  └─────────────────┘
   │ Lovelace  │
   │ Card      │
   └───────────┘
```

---

## Key Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Integration vs Addon | Custom Integration (HACS) | Needs direct entity access, no separate service needed |
| HVAC zones | Support both single-thermostat and multi-zone | Rooms can share a climate entity or have their own |
| Vent control | Recommendations + optional direct control | Works for manual vents, smart vents (Flair/Keen), or no vents |
| Weather source | User picks weather entity OR outdoor temp sensor | Maximum flexibility |
| LLM communication | Direct HTTP via aiohttp | Avoids heavy SDK dependencies in HA environment |
| Dashboard | Custom Lovelace card | Room overview, scores, AI suggestions, approval buttons |
| Data storage | HA long-term statistics + in-memory coordinator | Sensors with state_class auto-persist; coordinator holds live state |
| Schedules | Room-level named schedules with profiles | Baby nap, night, away, etc. - each with target temp, mode, and time windows |
| Auxiliary devices | Optional per-room space heaters/fans/portable ACs | Helps offset HVAC imbalances in specific rooms when primary HVAC can't keep up |

---

## File Structure

```
hass-climate-controll/
├── hacs.json
├── custom_components/
│   └── smart_climate/
│       ├── __init__.py              # Entry setup, service registration, lifecycle
│       ├── manifest.json            # HA/HACS metadata (2026.2 target)
│       ├── const.py                 # All constants, config keys, defaults, events
│       ├── config_flow.py           # Multi-step setup wizard + options flow
│       ├── strings.json             # Config flow strings
│       ├── translations/en.json     # English translations
│       ├── models.py                # Dataclasses: RoomConfig, RoomState, Suggestion, etc.
│       ├── coordinator.py           # SmartClimateCoordinator (DataUpdateCoordinator)
│       ├── entity.py                # SmartClimateEntity base class
│       ├── climate.py               # Virtual zone climate entities (proxy layer)
│       ├── sensor.py                # Comfort, efficiency, runtime, AI sensors
│       ├── binary_sensor.py         # Occupancy, window, comfort alert, suggestions pending
│       ├── services.py              # Service handler implementations
│       ├── services.yaml            # Service definitions
│       ├── diagnostics.py           # HA diagnostics (redact API keys)
│       ├── helpers/
│       │   ├── __init__.py
│       │   ├── comfort.py           # Comfort score algorithm
│       │   ├── efficiency.py        # Efficiency score, degree-day calculations
│       │   ├── presence.py          # Follow-me target determination
│       │   ├── vents.py             # Smart vent control + recommendations
│       │   ├── scheduling.py        # Room schedules engine (nap, night, away profiles)
│       │   ├── auxiliary.py         # Auxiliary device control (space heaters, fans, portable ACs)
│       │   └── statistics.py        # HA recorder/statistics query helpers
│       └── ai/
│           ├── __init__.py
│           ├── provider.py          # ABC, factory, NoOp, error classes
│           ├── openai_provider.py   # OpenAI GPT (direct HTTP)
│           ├── anthropic_provider.py # Anthropic Claude (direct HTTP)
│           ├── ollama_provider.py   # Ollama/llama.cpp (local HTTP)
│           ├── gemini_provider.py   # Google Gemini (direct HTTP)
│           ├── grok_provider.py     # xAI Grok (OpenAI-compatible HTTP)
│           ├── prompts.py           # System/user prompt templates
│           ├── analysis.py          # Response parsing, validation, sanitization
│           └── suggestions.py       # Suggestion lifecycle management
├── smart-climate-card/              # Custom Lovelace card
│   ├── package.json
│   ├── rollup.config.js             # or vite
│   ├── src/
│   │   ├── smart-climate-card.ts    # Main card element (LitElement)
│   │   ├── components/
│   │   │   ├── room-tile.ts         # Individual room tile component
│   │   │   ├── house-overview.ts    # Top-level house comfort/efficiency gauges
│   │   │   ├── suggestion-panel.ts  # AI suggestions with approve/reject UI
│   │   │   ├── schedule-view.ts     # Schedule timeline visualization
│   │   │   ├── room-detail.ts       # Expanded room detail modal/drawer
│   │   │   ├── efficiency-chart.ts  # SVG mini-charts for efficiency data
│   │   │   └── auxiliary-status.ts  # Auxiliary device status indicators
│   │   ├── styles/
│   │   │   ├── theme.ts             # CSS custom properties, dark/light mode
│   │   │   ├── card-styles.ts       # Main card layout styles
│   │   │   └── animations.ts        # Subtle transitions and micro-interactions
│   │   └── utils/
│   │       ├── ha-api.ts            # HA WebSocket helpers for service calls
│   │       └── formatters.ts        # Temp/time/score formatting utilities
│   └── dist/
│       └── smart-climate-card.js    # Built bundle (served by HA)
└── tests/
    ├── conftest.py
    ├── test_config_flow.py
    ├── test_coordinator.py
    ├── test_comfort.py
    ├── test_efficiency.py
    ├── test_ai_providers.py
    └── test_services.py
```

---

## Config Flow (Multi-Step Setup Wizard)

### Step 1: General Settings
- Integration name
- Temperature unit (F/C)
- Update interval (15-300s, default 60)
- Enable follow-me (bool)
- Enable auto zone balancing (bool)

### Step 2: Outdoor Weather
- Select weather entity OR outdoor temperature sensor
- Used for degree-day calcs, AI context, and efficiency analysis

### Step 3: Room Menu (add rooms, loop)
- Menu: "Add a Room" / "Finish Room Setup"
- Minimum 1 room required

### Step 4: Add Room (per room)
- Room name
- Climate entity selector (domain: climate) - **multiple rooms can share one climate entity**
- Temperature sensor(s) (multi-select)
- Humidity sensor(s) (optional, multi-select)
- Presence/motion sensor(s) (optional, multi-select)
- Door/window contact sensor(s) (optional, multi-select)
- Smart vent entities (optional, multi-select, domain: cover/switch/number)
- Auxiliary devices (optional, multi-select, domain: climate/switch/fan) - space heaters, fans, portable ACs
- Room priority (1-10, default 5)
- Target temp offset

### Step 5: Schedules
- Menu: "Add Schedule" / "Finish Schedule Setup" / "Skip"
- Per schedule:
  - Schedule name (e.g., "Baby Nap", "Night Mode", "Work Hours", "Away")
  - Rooms this schedule applies to (multi-select from configured rooms, or "all")
  - Days of week (multi-select: Mon-Sun)
  - Start time (HH:MM)
  - End time (HH:MM)
  - Target temperature for this schedule
  - HVAC mode override (optional: heat/cool/auto/off)
  - Enable auxiliary devices (bool - use space heaters/fans if room can't reach target)
  - Priority (1-10, higher priority schedules override lower ones when overlapping)
- Schedules are stored as a list in config entry data and can be managed via options flow

### Step 6: AI Provider
- Provider: OpenAI / Anthropic / Ollama / Gemini / Grok / None
- API key (not needed for Ollama)
- Model name
- Base URL (for Ollama/custom endpoints)
- Daily analysis time (HH:MM, default 06:00)
- Auto-apply high-confidence suggestions (bool, default false)
- Connection test on submit

### Options Flow (post-setup)
- Edit all above settings
- Manage rooms (add/edit/remove)
- Manage schedules (add/edit/remove)
- Advanced: comfort weights, efficiency thresholds, follow-me cooldown, away temp offset, window-open behavior, auxiliary device thresholds

---

## Entities Created

### Per-Room Sensors
| Entity | Type | Description |
|---|---|---|
| `sensor.sc_{room}_comfort_score` | sensor (%) | 0-100 comfort score |
| `sensor.sc_{room}_efficiency_score` | sensor (%) | 0-100 HVAC efficiency |
| `sensor.sc_{room}_temperature` | sensor (°F/°C) | Averaged room temp |
| `sensor.sc_{room}_humidity` | sensor (%) | Averaged room humidity |
| `sensor.sc_{room}_hvac_runtime` | sensor (min) | HVAC runtime today |
| `sensor.sc_{room}_hvac_cycles` | sensor (count) | On/off cycles today |
| `binary_sensor.sc_{room}_occupied` | binary_sensor | Room presence |
| `binary_sensor.sc_{room}_window_open` | binary_sensor | Any window/door open |
| `binary_sensor.sc_{room}_comfort_alert` | binary_sensor | Comfort below threshold |
| `sensor.sc_{room}_active_schedule` | sensor (text) | Currently active schedule name (or "none") |
| `binary_sensor.sc_{room}_auxiliary_active` | binary_sensor | Auxiliary device is running to help |
| `climate.sc_{room}` | climate | Virtual zone controller (proxy) |

### Whole-House Sensors
| Entity | Type | Description |
|---|---|---|
| `sensor.sc_house_comfort` | sensor (%) | Weighted average comfort |
| `sensor.sc_house_efficiency` | sensor (%) | Overall efficiency |
| `sensor.sc_house_hvac_runtime` | sensor (min) | Total runtime |
| `sensor.sc_heating_degree_days` | sensor (DD) | Accumulated HDD |
| `sensor.sc_cooling_degree_days` | sensor (DD) | Accumulated CDD |
| `sensor.sc_ai_last_analysis` | sensor (timestamp) | Last analysis time |
| `sensor.sc_ai_suggestion_count` | sensor (count) | Pending suggestions |
| `sensor.sc_ai_daily_summary` | sensor (text) | AI summary text |
| `sensor.sc_active_schedule` | sensor (text) | House-wide active schedule name |
| `binary_sensor.sc_suggestions_pending` | binary_sensor | Has pending suggestions |

### Virtual Climate Entity (per room)
- Proxies to the underlying real climate entity
- Adds Smart Climate control layer (follow-me targets, zone balancing)
- Tracks whether user has manually overridden the smart target
- Attributes: `underlying_entity`, `smart_target`, `user_override_active`, `follow_me_active`, `last_adjustment_reason`

---

## Services

| Service | Description |
|---|---|
| `smart_climate.trigger_analysis` | Run AI analysis now (scope: all/room) |
| `smart_climate.approve_suggestion` | Approve a suggestion by ID |
| `smart_climate.reject_suggestion` | Reject a suggestion by ID (optional reason) |
| `smart_climate.approve_all_suggestions` | Approve all pending |
| `smart_climate.reject_all_suggestions` | Reject all pending |
| `smart_climate.add_room` | Dynamically add a room |
| `smart_climate.remove_room` | Remove a room |
| `smart_climate.set_room_priority` | Change room priority |
| `smart_climate.force_follow_me` | Override follow-me to a specific room |
| `smart_climate.reset_statistics` | Reset runtime/cycle counters |
| `smart_climate.add_schedule` | Add a named schedule (rooms, days, time, temp) |
| `smart_climate.remove_schedule` | Remove a schedule by name |
| `smart_climate.activate_schedule` | Manually activate a schedule now (override) |
| `smart_climate.deactivate_schedule` | Deactivate a manual schedule override |
| `smart_climate.set_auxiliary_mode` | Enable/disable auxiliary devices for a room |

---

## Events Fired

| Event | When |
|---|---|
| `smart_climate_analysis_complete` | AI analysis finishes |
| `smart_climate_new_suggestions` | New suggestions created |
| `smart_climate_suggestion_applied` | Suggestion executed |
| `smart_climate_suggestion_rejected` | Suggestion rejected |
| `smart_climate_comfort_alert` | Comfort score below threshold |
| `smart_climate_efficiency_alert` | Efficiency problem detected |
| `smart_climate_follow_me_changed` | Follow-me target room changed |
| `smart_climate_window_open_adjusted` | HVAC adjusted for open window |
| `smart_climate_schedule_activated` | A schedule became active |
| `smart_climate_schedule_deactivated` | A schedule ended |
| `smart_climate_auxiliary_activated` | Auxiliary device turned on to help |
| `smart_climate_auxiliary_deactivated` | Auxiliary device turned off |

---

## AI Analysis Pipeline

1. **Trigger**: Daily schedule (configurable time) or manual service call
2. **Gather**: Last 24h of room temps, humidity, presence patterns, HVAC runtime, window events, outdoor weather, current setpoints, previous suggestion outcomes
3. **Serialize**: Build structured JSON payload, respect token limits, summarize if needed
4. **Prompt**: System prompt (role, constraints, output JSON schema) + user prompt (data payload)
5. **Call LLM**: Via provider abstraction (aiohttp direct HTTP), 3 retries with backoff, 120s timeout
6. **Parse**: Extract JSON from response, validate schema, sanitize actions (prevent dangerous service calls), assign UUIDs
7. **Store**: Suggestions queued with status=pending, expiry=24h
8. **Notify**: Fire events, update sensor entities
9. **Auto-apply**: If enabled AND confidence >= 0.8, execute immediately; otherwise queue for user approval
10. **Execute**: Approved suggestions become HA service calls (set_temperature, set_mode, etc.)

### LLM Provider Abstraction
- `AIProviderBase` ABC with `analyze(system_prompt, user_prompt) -> str` and `test_connection() -> bool`
- Factory function `create_ai_provider(type, config)` returns appropriate implementation
- Each provider makes direct HTTP calls via aiohttp (no SDK dependencies)
- `NoOpProvider` for when no AI is configured

---

## Smart Features

### Follow-Me (Ecobee-style)
- Monitors presence sensors across all rooms
- Determines primary occupied room (most recent activity + highest priority)
- Occupied rooms get comfort-priority temperature targets
- Unoccupied rooms get offset (configurable away_temp_offset, default ±4°)
- Cooldown prevents thrashing (default 10 min)
- Weighted phase-in like Ecobee (gradual, not instant)

### Zone Balancing
- Detects rooms over/under-conditioned relative to targets
- For shared-thermostat setups: adjusts the single thermostat based on weighted room priorities
- For multi-zone setups: adjusts individual zone targets
- Considers room thermal characteristics learned over time

### Smart Vent Control
- If smart vent entities configured: directly adjusts vent position (0-100%)
- If no smart vents: generates text recommendations ("Open living room vents to 80%, close bedroom to 40%")
- AI suggestions can include vent adjustment recommendations
- Static pressure awareness (won't close too many vents simultaneously)

### Window/Door Detection
- Open contact sensor → reduce HVAC effort (configurable: reduce target or switch to eco)
- Fire event for automation hooks
- AI considers window events in its analysis

### Room Schedules
Named, recurring temperature profiles per room with priority-based conflict resolution.

**Schedule Data Model:**
```python
@dataclass
class Schedule:
    name: str                          # "Baby Nap", "Night Mode", "Work Away"
    slug: str                          # auto-generated from name
    rooms: list[str]                   # room slugs, or ["__all__"] for whole house
    days: list[int]                    # 0=Mon through 6=Sun
    start_time: str                    # "13:00"
    end_time: str                      # "15:00"
    target_temperature: float          # 72.0
    hvac_mode: str | None              # optional override: "heat", "cool", "auto", "off"
    use_auxiliary: bool                 # activate auxiliary devices if HVAC can't keep up
    priority: int                      # 1-10, higher wins on overlap
    enabled: bool                      # can be toggled without deleting
```

**Schedule Engine Logic (helpers/scheduling.py):**
1. Every coordinator update (60s), evaluate which schedules are currently active
2. For each room, find all applicable active schedules (matching room, day, time window)
3. If multiple schedules overlap, highest priority wins; if tied, most specific (single room > all rooms) wins
4. Active schedule overrides follow-me and zone balancing targets for that room
5. If `use_auxiliary` is true and room is > 2° from schedule target after 15 min, engage auxiliary devices
6. Schedules fire `smart_climate_schedule_activated` / `smart_climate_schedule_deactivated` events
7. AI analysis receives schedule data and can suggest schedule adjustments

**Use Cases:**
- Baby nap: Nursery at 70°F, 1pm-3pm weekdays, high priority, use space heater if needed
- Night mode: All rooms at 66°F, 10pm-6am daily
- Work away: All rooms at 62°F, 8am-5pm weekdays (lower priority than baby nap)
- Weekend morning: Living room at 72°F, 7am-10am Sat-Sun

### Auxiliary Device Control
Secondary climate helpers (space heaters, fans, portable ACs) that supplement the primary HVAC when it can't keep a room at target.

**Supported Device Types (by HA domain):**
- `climate` domain: Portable ACs, space heaters with climate entities (full temperature control)
- `switch` domain: Simple on/off space heaters, fans (binary control)
- `fan` domain: Fans with speed control (percentage-based)
- `number` domain: Devices with adjustable power levels

**Auxiliary Control Logic (helpers/auxiliary.py):**
1. Per room, user configures zero or more auxiliary device entities during room setup
2. Auxiliary devices are ONLY engaged when:
   a. The room is > `auxiliary_threshold` degrees from target (default: 2°) AND
   b. The primary HVAC has been running for > `auxiliary_delay_minutes` (default: 15 min) AND
   c. Temperature trend shows HVAC is losing or not gaining
3. Engagement is gradual:
   - For `switch` entities: turn on
   - For `climate` entities: set to same target temp as room schedule/follow-me target
   - For `fan` entities: set speed proportional to temperature deviation (25% per degree)
4. Disengagement when room is within 1° of target (hysteresis to prevent cycling)
5. Safety: configurable max runtime for auxiliary devices (default: 2 hours continuous)
6. AI analysis includes auxiliary device usage in efficiency reports and can suggest when auxiliaries are being over-relied on (indicating HVAC or insulation issues)

**Auxiliary Entity Attributes (on binary_sensor.sc_{room}_auxiliary_active):**
```
active_devices: ["switch.nursery_space_heater", "fan.bedroom_fan"]
reason: "Room 3.2° below schedule target after 18 min HVAC runtime"
runtime_minutes: 22
auto_shutoff_at: "2026-02-10T15:30:00"
```

---

## Custom Lovelace Card - Detailed Design

### Design Philosophy
Modern, clean, glassmorphism-inspired design that follows HA's Material Design language but adds visual richness. The card should feel like a premium smart home dashboard — information-dense but not cluttered, with clear visual hierarchy and satisfying micro-interactions.

### Color System
```
Comfort Score Colors (gradient):
  90-100: #10B981 (emerald green)    "Excellent"
  70-89:  #3B82F6 (blue)             "Good"
  50-69:  #F59E0B (amber)            "Fair"
  30-49:  #F97316 (orange)           "Poor"
  0-29:   #EF4444 (red)              "Critical"

HVAC Action Colors:
  Heating: #EF4444 (warm red) with subtle glow
  Cooling: #3B82F6 (cool blue) with subtle glow
  Idle:    var(--secondary-text-color)
  Off:     var(--disabled-text-color)

Background:
  Light mode: rgba(255,255,255,0.8) with backdrop-filter: blur(10px)
  Dark mode:  rgba(30,30,30,0.8) with backdrop-filter: blur(10px)
```

### Card Layout (Top to Bottom)

#### 1. Header Bar
```
┌──────────────────────────────────────────────────┐
│  🏠 Smart Climate              ⚙️  │  ···       │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  House Comfort: 82%  ●●●●●●●●○○  Efficiency: 74%│
│                                                  │
│  HVAC: Heating ◉  |  Follow-Me: Living Room 👤   │
│  Active Schedule: Night Mode (until 6:00 AM)     │
└──────────────────────────────────────────────────┘
```
- House comfort as a segmented progress bar (color-coded)
- Efficiency as a segmented progress bar
- Current HVAC action with animated dot (pulses when heating/cooling)
- Follow-me target room with presence icon
- Active schedule name with countdown/end time
- Settings gear opens options flow, `···` opens detail view

#### 2. Room Grid (Responsive 2-3 column grid)
Each room is a tile card:
```
┌─────────────────────────┐
│  Living Room        👤  │  ← room name + occupancy dot
│                         │
│     72.1°F              │  ← large current temp
│     ↗ +0.3°/hr          │  ← trend arrow + rate
│                         │
│  💧 45%    🎯 72°F      │  ← humidity + target temp
│                         │
│  Comfort ━━━━━━━━━━░░ 84│  ← mini progress bar + score
│                         │
│  ❄️ Cooling  ⏱ 42min    │  ← HVAC action + runtime today
│  📅 Baby Nap (→3:00 PM) │  ← active schedule if any
│  🔌 Space Heater: ON    │  ← auxiliary status if active
└─────────────────────────┘
```
- Tile background has subtle gradient based on comfort score color
- Occupied rooms have a soft glow border (green)
- Follow-me target room has a highlighted border (blue pulse)
- Clicking a tile opens the Room Detail drawer
- Window-open rooms show a small window icon with warning color
- Auxiliary device status shown only when active

#### 3. Schedule Timeline (Collapsible Section)
```
┌──────────────────────────────────────────────────┐
│  📅 Today's Schedules                    ▼       │
│                                                  │
│  ┃ 6AM    9AM    12PM   3PM    6PM    9PM   12AM│
│  ┃━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━│
│  ┃ Nursery:                                     │
│  ┃         ▓▓▓▓▓▓▓           ▓▓▓▓▓▓▓           │
│  ┃      Baby Nap 70°F    Baby Nap 70°F          │
│  ┃ All Rooms:                                   │
│  ┃ ░░░░░░                              ▓▓▓▓▓▓▓▓│
│  ┃ Night 66°F                          Night 66°│
│  ┃                ▒▒▒▒▒▒▒▒▒▒                    │
│  ┃              Work Away 62°F                   │
│  ┃                                              │
│  ┃  ▲ NOW                                       │
└──────────────────────────────────────────────────┘
```
- Horizontal timeline showing all schedules for the day
- Color-coded blocks per schedule
- "NOW" marker shows current time position
- Overlapping schedules shown with priority indicator
- Click a block to edit that schedule

#### 4. AI Suggestions Panel (Collapsible Section)
```
┌──────────────────────────────────────────────────┐
│  🤖 AI Suggestions (3 pending)           ▼       │
│                                                  │
│  ┌────────────────────────────────────────────┐  │
│  │ 🌡️ Nursery: Lower to 69°F during naps     │  │
│  │ The nursery averages 71.2°F during nap     │  │
│  │ schedule but baby sleeps better at 69°F    │  │
│  │ based on 2-week pattern.                   │  │
│  │ Confidence: ●●●●○ 85%   Priority: High    │  │
│  │                                            │  │
│  │  [ ✓ Approve ]  [ ✗ Reject ]  [ ··· ]    │  │
│  └────────────────────────────────────────────┘  │
│                                                  │
│  ┌────────────────────────────────────────────┐  │
│  │ 🔧 Guest Bedroom: Close vents to 30%       │  │
│  │ This room is consistently 3°F above target │  │
│  │ while adjacent office is 2°F below.        │  │
│  │ Confidence: ●●●○○ 72%   Priority: Medium  │  │
│  │                                            │  │
│  │  [ ✓ Approve ]  [ ✗ Reject ]  [ ··· ]    │  │
│  └────────────────────────────────────────────┘  │
│                                                  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  [ ✓ Approve All ]        [ ✗ Reject All ]       │
│                                                  │
│  Last analysis: Today 6:00 AM (Anthropic Claude) │
│  Daily summary: Your HVAC ran 18% less than...   │
└──────────────────────────────────────────────────┘
```
- Each suggestion is a card with icon, description, reasoning, confidence dots, priority badge
- Approve/Reject buttons call services via WebSocket
- `···` menu: view details, mark as "don't suggest again"
- Bottom shows last analysis timestamp, provider used, and truncated daily summary
- Expand summary to see full AI analysis text

#### 5. Room Detail Drawer (opens on room tile click)
```
┌──────────────────────────────────────────────────┐
│  ← Living Room                           ✕       │
│                                                  │
│  ┌──────────────┐  ┌──────────────┐              │
│  │  72.1°F      │  │  45%         │              │
│  │  Temperature  │  │  Humidity    │              │
│  │  ↗ +0.3°/hr  │  │  → stable    │              │
│  └──────────────┘  └──────────────┘              │
│                                                  │
│  Comfort: ━━━━━━━━━━━░░░ 84%                    │
│  Efficiency: ━━━━━━━━░░░░░ 68%                   │
│                                                  │
│  ── Climate Control ──────────────────────────   │
│  Target: [  72  ] °F   Mode: [ Auto ▼ ]         │
│  Smart Target: 72°F (follow-me active)           │
│  Underlying: climate.ecobee_living_room          │
│                                                  │
│  ── HVAC Today ───────────────────────────────   │
│  Runtime: 2h 42min  │  Cycles: 8                 │
│  ▁▃▅▇▅▃▁▃▅▇▅▃▁▃▅   (mini runtime bar chart)     │
│                                                  │
│  ── Auxiliary Devices ────────────────────────   │
│  Space Heater (switch.lr_heater): Off            │
│  Standing Fan (fan.lr_fan): Off                  │
│                                                  │
│  ── Sensors ──────────────────────────────────   │
│  Temp: sensor.lr_temp (72.1°F)                   │
│  Humidity: sensor.lr_humidity (45%)              │
│  Presence: binary_sensor.lr_motion (Detected)    │
│  Window: binary_sensor.lr_window (Closed)        │
│                                                  │
│  ── Active Schedule ──────────────────────────   │
│  None (follow-me mode active)                    │
│                                                  │
│  ── Vents ────────────────────────────────────   │
│  Smart Vent: cover.lr_vent (85% open)            │
└──────────────────────────────────────────────────┘
```

### Tech Stack
- **LitElement** (standard for HA custom cards)
- **TypeScript** (type-safe, better DX)
- **Lit HTML** templates (native HA pattern)
- **Vite** bundler (fast builds)
- **HA WebSocket API** for service calls (approve/reject, temp changes)
- **CSS Custom Properties** - inherits HA theme variables for dark/light mode compatibility
- **CSS Grid + Container Queries** - responsive room grid (2 cols on medium, 3 on wide, 1 on narrow)

### Card Configuration (YAML)
```yaml
type: custom:smart-climate-card
entity: sensor.sc_house_comfort  # Required: links to integration
show_schedule: true              # Show timeline section
show_suggestions: true           # Show AI panel
show_efficiency: true            # Show efficiency data
columns: auto                    # auto, 2, or 3
compact: false                   # Compact mode for smaller dashboards
rooms_order:                     # Optional room ordering
  - living_room
  - nursery
  - bedroom
```

---

## Implementation Phases

### Phase 1: Foundation
**Files**: `hacs.json`, `manifest.json`, `const.py`, `models.py`, `__init__.py`, `config_flow.py`, `strings.json`, `translations/en.json`, `entity.py`
**Goal**: Installable integration, full config flow wizard works, config entry created with correct data shape.

### Phase 2: Coordinator + Core Sensors
**Files**: `coordinator.py`, `sensor.py`, `helpers/comfort.py`, `helpers/efficiency.py`, `helpers/__init__.py`
**Goal**: Coordinator polls all tracked entities every 60s. Room temp/humidity/comfort/efficiency sensors appear in HA and update.

### Phase 3: Binary Sensors + HVAC Tracking
**Files**: `binary_sensor.py`, update `coordinator.py` (HVAC cycle tracking), update `helpers/efficiency.py` (full efficiency with cycles)
**Goal**: Occupancy, window, comfort alert binary sensors work. HVAC runtime/cycles accumulate correctly.

### Phase 4: Virtual Climate + Follow-Me + Zone Balancing + Vents
**Files**: `climate.py`, `helpers/presence.py`, `helpers/vents.py`, update `coordinator.py`
**Goal**: Virtual climate entities proxy real ones. Follow-me adjusts targets on presence changes. Zone balancing works. Smart vent control operational.

### Phase 5: Schedules + Auxiliary Devices
**Files**: `helpers/scheduling.py`, `helpers/auxiliary.py`, update `coordinator.py`, update `sensor.py` (schedule sensors), update `binary_sensor.py` (auxiliary sensors), update `config_flow.py` (schedule step), update `models.py` (Schedule dataclass)
**Goal**: Named schedules created in config flow. Schedule engine evaluates active schedules each update cycle. Auxiliary devices engage when rooms can't reach schedule targets. Schedule/auxiliary entities appear in HA.

### Phase 6: AI Pipeline
**Files**: All `ai/` files (provider.py, openai_provider.py, anthropic_provider.py, ollama_provider.py, gemini_provider.py, grok_provider.py, prompts.py, analysis.py, suggestions.py), update `coordinator.py`
**Goal**: LLM analysis runs daily and on-demand. Structured suggestions generated and stored.

### Phase 7: Services + Events + Approval Workflow
**Files**: `services.py`, `services.yaml`, update `__init__.py`, update `coordinator.py`, update `sensor.py` (AI sensors)
**Goal**: All services callable (including schedule and auxiliary services). Events fire. Suggestions can be approved/rejected/auto-applied.

### Phase 8: Custom Lovelace Card
**Files**: All `smart-climate-card/` files
**Goal**: Full modern dashboard card with room grid, schedule timeline, AI suggestion panel, room detail drawer, auxiliary device status. Dark/light mode support. Responsive layout.
**Sub-steps**:
  1. Project scaffolding (Vite + TypeScript + LitElement)
  2. Theme system and CSS custom properties
  3. House overview header component
  4. Room tile grid component
  5. Schedule timeline component
  6. AI suggestions panel component
  7. Room detail drawer component
  8. WebSocket service call integration
  9. Build + bundle as single JS file

### Phase 9: Statistics + Diagnostics + Testing
**Files**: `helpers/statistics.py`, `diagnostics.py`, all `tests/` files
**Goal**: Long-term statistics persist. Diagnostics work. Test suite passes. HACS validation passes.

---

## Verification Plan

1. **Phase 1**: Install via HACS dev, walk through full config flow, verify config entry data in `.storage`
2. **Phase 2**: Confirm sensor entities appear in HA, values update every 60s, comfort scores compute
3. **Phase 3**: Toggle motion sensors → verify occupancy binary sensors. Open/close doors → window sensor. Watch HVAC runtime accumulate
4. **Phase 4**: Walk between rooms → follow-me changes target. Verify virtual climate entities mirror and proxy real ones. Configure smart vents → verify position changes
5. **Phase 5**: Create schedules (baby nap, night mode). Verify schedule activates at correct time, target temps adjust. Configure auxiliary device → verify it engages when room can't reach target. Verify schedule/auxiliary sensors update
6. **Phase 6**: Configure AI provider, call `smart_climate.trigger_analysis`, verify structured JSON response and suggestions created. Verify AI receives schedule data in context
7. **Phase 7**: Approve/reject suggestions via Developer Tools → Services. Verify events in Developer Tools → Events. Test schedule and auxiliary services
8. **Phase 8**: Add card to dashboard. Verify: room tiles render with correct data, schedule timeline shows today's schedules, suggestion panel approve/reject works, room detail drawer opens on click, dark/light mode both look correct, responsive layout at different widths
9. **Phase 9**: Run `pytest tests/`, check HA long-term statistics, download diagnostics
