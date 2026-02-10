# Smart Climate

AI-powered climate control for Home Assistant. Works with **any** climate entity — combines temperature, humidity, presence, and door/window sensors per room with LLM-driven analysis to keep your home comfortable and efficient.

## Features

- **Room-based climate zones** — group sensors and climate entities by room, even when multiple rooms share one thermostat
- **Comfort & efficiency scoring** — real-time 0-100 scores for every room and the whole house
- **Follow-me mode** — automatically adjusts targets based on which rooms are occupied (like Ecobee, but device-agnostic)
- **Zone balancing** — smart vent control and thermostat adjustments to even out hot/cold spots
- **Room schedules** — named recurring profiles (Baby Nap, Night Mode, Work Away) with priority-based conflict resolution
- **Auxiliary device control** — engages space heaters, fans, and portable ACs when HVAC can't keep up
- **AI suggestions** — daily LLM analysis generates actionable suggestions you approve before they're applied
- **5 AI providers** — OpenAI, Anthropic, Ollama (local), Google Gemini, xAI Grok
- **Custom Lovelace card** — room grid, schedule timeline, AI suggestion panel with approve/reject buttons

## Installation (HACS)

The integration and Lovelace card are installed together — one repo, one install.

1. Open HACS in Home Assistant
2. Click the **three dots** menu (top right) → **Custom repositories**
3. Add this repository URL:
   ```
   https://github.com/JoshuaSeidel/smart-climate-ha
   ```
4. Select category: **Integration**
5. Click **Add**
6. Search for **Smart Climate** in HACS → **Download**
7. Restart Home Assistant
8. Go to **Settings → Devices & Services → Add Integration → Smart Climate**
9. Walk through the setup wizard:
   - General settings (temp unit, update interval, follow-me, zone balancing)
   - Outdoor weather source
   - Add rooms (climate entity, sensors, vents, auxiliary devices)
   - Add schedules (optional)
   - AI provider (optional)

The custom Lovelace card is bundled with the integration and auto-registered — no separate install needed. After setup, add it to any dashboard:

```yaml
type: custom:smart-climate-card
entity: sensor.sc_house_comfort
show_schedule: true
show_suggestions: true
show_efficiency: true
```

### Manual Installation

**Integration + Card:**
Copy `custom_components/smart_climate/` into your Home Assistant `config/custom_components/` directory and restart. The card JS is served automatically from `custom_components/smart_climate/www/`.

**Building the card from source** (for development):
```bash
cd smart-climate-card
npm install
npm run build
cp dist/smart-climate-card.js ../custom_components/smart_climate/www/
```

## Card Configuration

```yaml
type: custom:smart-climate-card
entity: sensor.sc_house_comfort   # Required — links card to integration
show_schedule: true                # Show schedule timeline section
show_suggestions: true             # Show AI suggestions panel
show_efficiency: true              # Show efficiency data
columns: auto                      # auto, 2, or 3
compact: false                     # Compact mode for smaller dashboards
rooms_order:                       # Optional room display order
  - living_room
  - nursery
  - bedroom
```

## Entities Created

### Per Room
| Entity | Description |
|---|---|
| `sensor.sc_{room}_comfort_score` | 0-100 comfort score |
| `sensor.sc_{room}_efficiency_score` | 0-100 HVAC efficiency |
| `sensor.sc_{room}_temperature` | Averaged room temperature |
| `sensor.sc_{room}_humidity` | Averaged room humidity |
| `sensor.sc_{room}_hvac_runtime` | HVAC runtime today (minutes) |
| `sensor.sc_{room}_hvac_cycles` | On/off cycles today |
| `sensor.sc_{room}_active_schedule` | Currently active schedule name |
| `binary_sensor.sc_{room}_occupied` | Room occupancy |
| `binary_sensor.sc_{room}_window_open` | Any window/door open |
| `binary_sensor.sc_{room}_comfort_alert` | Comfort below threshold |
| `binary_sensor.sc_{room}_auxiliary_active` | Auxiliary device running |
| `climate.sc_{room}` | Virtual zone controller (proxies real entity) |

### Whole House
| Entity | Description |
|---|---|
| `sensor.sc_house_comfort` | Weighted average comfort |
| `sensor.sc_house_efficiency` | Overall efficiency |
| `sensor.sc_house_hvac_runtime` | Total runtime |
| `sensor.sc_heating_degree_days` | Heating degree days |
| `sensor.sc_cooling_degree_days` | Cooling degree days |
| `sensor.sc_ai_last_analysis` | Last AI analysis timestamp |
| `sensor.sc_ai_suggestion_count` | Pending suggestion count |
| `sensor.sc_ai_daily_summary` | AI summary text |
| `sensor.sc_active_schedule` | House-wide active schedule |
| `binary_sensor.sc_suggestions_pending` | Has pending suggestions |

## Services

| Service | Description |
|---|---|
| `smart_climate.trigger_analysis` | Run AI analysis now |
| `smart_climate.approve_suggestion` | Approve a suggestion by ID |
| `smart_climate.reject_suggestion` | Reject a suggestion by ID |
| `smart_climate.approve_all_suggestions` | Approve all pending |
| `smart_climate.reject_all_suggestions` | Reject all pending |
| `smart_climate.set_room_priority` | Change room priority |
| `smart_climate.force_follow_me` | Override follow-me target |
| `smart_climate.reset_statistics` | Reset runtime/cycle counters |
| `smart_climate.add_schedule` | Add a named schedule |
| `smart_climate.remove_schedule` | Remove a schedule |
| `smart_climate.activate_schedule` | Manually activate a schedule |
| `smart_climate.deactivate_schedule` | Deactivate a schedule override |
| `smart_climate.set_auxiliary_mode` | Enable/disable auxiliary for a room |

## Requirements

- Home Assistant 2026.2+
- HACS (for easy installation)
- At least one climate entity
- Optional: AI provider API key (OpenAI, Anthropic, Gemini, Grok) or local Ollama instance

## License

MIT
