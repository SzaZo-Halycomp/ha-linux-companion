# Session handoff — HA Linux Companion (x86 panel work)

Written 2026-11-02 at the end of a Claude Code session started 2026-10-26 on the user's
laptop (`/srv/omnIQ/ha-linux-companion`). Use it to continue on another machine.

## The user

- Works in a Hungarian Home Assistant setup; writes short English messages, often terse
  ("done", "push it", "waiot" = wait). Tests things live on the panel while Claude works.
- Wants changes tested on the real running app and HA, and pushed to the fork only when
  they say so ("push it"). Asked to hold the latest changes until they finish testing.
- GitHub: `SzaZo-Halycomp`; email `dealer@ddsweb.hu` (commit identity).

## Repos

- `origin` = https://github.com/SzaZo-Halycomp/ha-linux-companion (the user's fork).
- Upstream = https://github.com/SimoneB79/ha-linux-companion (Italian author, Pi-first).
  The fork was synced (fast-forward) to upstream `59dcef2` (v3.0.5) on 2026-10-26, then
  the commits below were added on top. Upstream has none of them.

## Environments

**Laptop where this session ran** (dev/test panel)
- HP EliteBook 840 G6, Debian 13 (trixie), KDE Plasma **Wayland**, user `szazo` (uid 1000).
- `intel_backlight` (max 24000), battery `BAT0` + `AC`, PipeWire (Realtek ALC215 / SOF;
  sinks Speaker + HDMI1-3), Wi-Fi `wlp58s0` = 172.16.201.180.
- Node 20.20.2 installed user-local in `~/.local/opt/node` (no system Node, no Docker).
- udev backlight rule installed, user in `video`; git `credential.helper store` set (token
  in `~/.git-credentials`), no global git user.name/email.
- Repo checkout `/srv/omnIQ/ha-linux-companion` (chowned to szazo). The app was started
  by hand (not installed to /opt, no autostart on this laptop).
- `/srv/omnIQ/srv/full/ha-linux-companion` = older upstream v2.5.0 clone with the user's
  original uncommitted x86 + Docker experiments (host X11 socket, mutter xauth, uid 1000,
  network_mode host, system dbus). The x86 parts are now ported properly; the Docker
  host-X11 variant was NOT ported.

**Home Assistant**: `http://192.168.201.10:8123`, UI language Hungarian.
- This laptop's device: name `test-classys` → `notify.mobile_app_test_classys`.
- Another panel exists: `notify.mobile_app_omniqpanel_sajkod`.
- TTS engines `tts.piper`, `tts.edge_tts`, `tts.edge_tts_2` — on 2026-10-26 Piper and
  `tts.edge_tts` returned HTTP 500 from `/api/tts_get_url`; `tts.edge_tts_2` returned a
  `/api/tts_proxy/...mp3` path but HA never served the file (hung >2 min). HA-side issue.

**Other machine**: the user cloned the fork there and will install with
`sudo HA_HOST_WAIT=none bash install.sh` + desktop auto-login (instructions were given:
autostart `.desktop` only; do not also enable the systemd unit → two instances).

## Commits pushed to origin/main (2026-10-26)

| Commit | What |
|---|---|
| `6bf4ea8` | x86: generic sysfs backlight helpers, `bl_power` display state, x64 build targets + `build:x64`, `run.sh` Wayland socket autodetect |
| `a14bb3d` | Volume/mute via `pactl` default sink on PipeWire/PulseAudio (was ALSA Master; 40% hw showed as 22% in KDE) |
| `ac95c1f` | Hungarian locale; language default HA → system → English (was always Italian) |
| `0590679` | Re-inject overlay/i18n/toasts/kiosk CSS on every reload (language change killed settings) |
| `beb328b` | Top bar reveals after 2 s mouse dwell (`MOUSE_REVEAL_DELAY`), remaining strings translated, audio outputs via `pactl -f json` (short names), sidebar hidden via HA dock mode |
| `f30f5c3` | Battery: `battery_level` / `battery_state` sensors, top bar gauge, settings tile |
| `1d0cdbd` | Websocket push channel never connected (`wsConnecting` stuck true); `getLocalIP()` only knew eth/wlan/end → push_url was 127.0.0.1, IP sensor missing |
| `89f8986` | Websocket ids must increase (`wsMsgId`); fixed-id confirms made HA drop the channel after the first command |
| `b426d02` | `command_update_sensors` (undefined fn), `command_dnd` + notification settings actually applied (main-side `notif-settings.json`), `command_set_wallpaper` quoting |

## Pushed 2026-11-02 (after the user tested)

`1e5cbff` feat: play/stop audio commands + Home Assistant test YAMLs, then this `.claude/` folder.

- `src/main.js`: **`command_play_audio`** (`data: {url, volume 0..1}`) and
  **`command_stop_audio`** — hidden BrowserWindow + `new Audio()`, `/path` resolved
  against HA URL. Tested: internet mp3 plays (Chromium stream on Speaker), stop works,
  new play replaces the old one. HA TTS path test failed only because HA's TTS is broken.
- `examples/home-assistant/panel_command_script.yaml` — `script.panel_command`
  (fields: command, data, title, target; default target `mobile_app_test_classys`).
- `examples/home-assistant/panel_test_card.yaml` — manual card, 22 buttons calling the
  script (display, audio incl. play/stop, bluetooth, notifications/DND/critical, page
  navigation, open URL, wallpaper, update sensors, reload, restart, unknown command).
  The user tested the script + card in HA: "yamls looks good" (2026-11-02).
- `examples/home-assistant/commands/*.yaml` — 20 standalone Developer tools → Actions
  snippets, one per command/variant (screen_off/on, brightness, volume, play/stop audio,
  dnd_on/off, bluetooth_on/off, update_sensors, navigate(_home), open_url,
  reload_dashboard, set_wallpaper, restart_app, set_theme (with warning), notification,
  notification_critical).
- All examples use the placeholder `mobile_app_CHANGE_TO_ACTUAL_DEVICENAME` (user's request:
  no hard-coded device name); on this laptop it is `mobile_app_test_classys`.
- `.claude/` — these handoff files (committed separately; the fork is public, the user
  agreed to push them).

Nothing is uncommitted at the time of writing.

## Remote commands (all in `handleNotificationCommand`, src/main.js)

Send with `action: notify.mobile_app_<device>`, `data: {message: <command>, data: {...}}`.

| message | inner data | tested 2026-10-26 |
|---|---|---|
| `command_screen_off` / `command_screen_on` | — | ✔ via HA (bl_power 1/0) |
| `command_screen_brightness_level` | `brightness` 10–100 | ✔ (50 → 12000/24000) |
| `command_volume_level` | `volume_level` 0–1 | ✔ (PipeWire 0.30) |
| `command_dnd` | `dnd` true/false/"on"/"off" | ✔ (history only while on; `priority: critical` bypasses) |
| `command_bluetooth` | `bluetooth` turn_on/turn_off | ✔ |
| `command_update_sensors` | — | ✔ |
| `command_navigate` | `navigate` (HA path) | ✔ |
| `command_open_url` | `url` (needs `https://`) | ✔ (user tested index.hu) |
| `command_reload_dashboard` | — | ✔ overlay re-injected |
| `command_set_wallpaper` | `url` | ✔ (only visible where the dashboard has no own background) |
| `command_restart_app` | — | ✔ relaunch + reconnect ~2 s |
| `command_play_audio` / `command_stop_audio` | `url`, `volume` | ✔ |
| `command_set_theme` | `theme` | ✘ not tested on purpose: `frontend.set_theme` changes the theme for ALL HA users |

Plain messages (no `command_` prefix) show a toast; `title` beside `message`,
`priority` inside `data`.

## Open ideas / known gaps (not started)

- `command_open_url`: optionally prepend `https://` when the scheme is missing (offered).
- Crash restart: autostart doesn't restart a crashed app; offered a user systemd service
  with `Restart=always` used by install.sh instead of the autostart entry.
- Mute button initial state is not read from the system (always shows "off" on open).
- `install.sh` copies the repo to `/opt`; updating = `git pull` + rerun installer.
- Docker host-X11 setup from `srv/full` not ported.
- HA TTS on the server is broken (see above) — user should check HA logs.
- Night schedule / `display_state` sensor: `display_state` reports window existence, not
  the backlight; could use `getDisplayState()` instead.

## Gotchas learned

- Electron reorders argv → `pkill -f 'electron . '` misses; match `[e]lectron/dist/electron`
  and exclude `--type=` children.
- `--ozone-platform-hint=auto` picks X11 when started outside the session (DISPLAY set,
  no XDG_SESSION_TYPE) and Xwayland rejects it; `run.sh` now exports WAYLAND_DISPLAY /
  XDG_SESSION_TYPE when `$XDG_RUNTIME_DIR/wayland-0` exists.
- `chrome-sandbox` must be root-owned setuid for sandboxing; dev runs use `--no-sandbox`.
- When simulating mouse input over CDP the user's real mouse interferes (they test live).
- HA `mobile_app` re-registration every 60 s also updates sensor icons.
- `pactl get-sink-property` does not exist; use `pactl -f json list sinks`.
- `amixer` on this laptop drives the card's hardware Master (0–87 range), which PipeWire
  maps through a dB curve.
