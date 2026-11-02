# HA Linux Companion — project notes for Claude

Electron kiosk app that shows a Home Assistant dashboard on a Linux panel and registers
itself as a HA `mobile_app` device (sensors, notifications, remote commands).
This repo is the user's fork **SzaZo-Halycomp/ha-linux-companion** (`origin`) of
**SimoneB79/ha-linux-companion** (upstream, Raspberry Pi oriented). The fork adds x86
support and many fixes — see `.claude/HANDOFF.md` for history, current state and open items.

Read `.claude/HANDOFF.md` first when continuing work.

## Layout

- `src/main.js` — almost everything (single ~2200-line file): `HAClient` (registration,
  webhook), `collectSensors()`, `loadDashboard()` → `did-finish-load` → `injectUI()`,
  websocket push channel (`connectNotifications`), `handleNotificationCommand()`
  (all `command_*`), `showNotification()`, system helpers, IPC handlers, tray.
- `src/views/overlay.js` — injected into the HA page: top bar (clock, temp, battery, ⚙),
  settings side panel. Uses `t()` + `window.__haLocales` / `window.__haLang`.
- `src/views/toast.js` / `toast.css` — notification popups (injected).
- `src/views/login.html` — first-run login page (local file, own origin).
- `src/preload.js` — `window.haCompanion.*` IPC bridge used by overlay/login.
- `src/locales/{en,it,de,hu}/translation.json` — **all four must have the same keys**
  (64 keys now). Add every new string to all four.
- `install.sh` — Debian installer (Node 20, deps, copies repo to `/opt/ha-linux-companion`,
  autostart `.desktop`, `run.sh`, optional systemd unit). Profiles `raspi` / `generic`.
- `examples/home-assistant/` — HA script `panel_command` + test dashboard card.

## How the pieces fit (non-obvious)

- UI injection runs on **every** full page load via `injectUI()` (kiosk sidebar hide,
  i18n, overlay, toast). Overlay/toast guard against double injection with window flags.
  Sensors + websocket start only on the first dashboard load (`dashboardLoaded`).
- Language: saved `ha_lang` (page localStorage) → HA `selectedLanguage` → `<html lang>`
  → `navigator.language` → `en`. `SUPPORTED_LANGS` in main.js.
- Sidebar is hidden via HA's own `hass-dock-sidebar` event / `dockedSidebar=always_hidden`
  (CSS cannot reach HA's shadow DOM).
- Remote commands arrive over the HA websocket push channel. **Websocket message ids must
  strictly increase per connection** (`++wsMsgId`) — reused ids make HA reject the push
  confirm, tear down the channel after 10 s and fall back to `push_url` (unreachable).
  An exception inside a command handler also skips the confirm → same failure.
- `push_url` fallback uses `getLocalIP()` (any non-virtual interface) + a random port.
- Display: `setDisplayPower()` tries `vcgencmd` (Pi) → sysfs `bl_power` → `xset dpms`.
  Brightness: sysfs backlight (`findBacklight()`, prefers rpi-backlight) → `ddcutil`.
  Sysfs writes fall back to `sudo -n tee`. Needs the udev rule (below) on x86.
- Volume: `pactl` default sink when PipeWire/PulseAudio, `amixer Master` otherwise.
- Notification settings (enabled/sound/dnd/duration/melody) live in main:
  `~/.config/ha-linux-companion/notif-settings.json`, IPC `get/set-notif-settings`.
- `command_play_audio` plays in a hidden `BrowserWindow` (about:blank) via `new Audio()`;
  URLs starting with `/` are resolved against the HA URL.
- Config dir (also Electron userData): `~/.config/ha-linux-companion/` — `config.json`
  holds HA tokens + `deviceId`/`webhookId`: never print, commit or copy it between machines.

## Dev workflow

- Node 20+. If not system-wide, a user-local one works (`~/.local/opt/node/bin`).
- `npm install`; if `node_modules/electron/dist/electron` is missing run
  `node node_modules/electron/install.js` (npm sometimes skips the extract).
- Run: `.claude/tools/run-dev.sh` (handles Wayland/X11 env; add
  `--remote-debugging-address=127.0.0.1 --remote-debugging-port=9333` for CDP).
- Electron reorders argv, so find the main process with
  `ps -eo pid,args | grep '[e]lectron/dist/electron' | grep -v -- --type=` (not `pkill -f 'electron . '`).
- Logs: `~/.config/ha-linux-companion/app.log` (plus stdout of the launch).
- Syntax check: `node --check src/main.js src/views/overlay.js src/preload.js`.
- Test helpers in `.claude/tools/` (see README there): send HA notify commands, evaluate
  JS in the running page over CDP, take screenshots.
- Test against the **real running app** and HA; the user expects verified results
  (screenshots, log lines, sysfs/pactl readings), not assumptions.

## Host setup for x86 panels

```bash
# backlight write access for the video group (+ user in group video)
echo 'ACTION=="add", SUBSYSTEM=="backlight", RUN+="/bin/chgrp video /sys/class/backlight/%k/brightness /sys/class/backlight/%k/bl_power", RUN+="/bin/chmod g+w /sys/class/backlight/%k/brightness /sys/class/backlight/%k/bl_power"' | sudo tee /etc/udev/rules.d/90-backlight.rules
sudo udevadm trigger --action=add -s backlight   # plain "trigger" sends "change" and does nothing
sudo usermod -aG video $USER
```

## Git conventions

- Work on `main`, push to `origin` (the fork). Commit messages: `type: summary` +
  body explaining the why; end with
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- If no global git identity is set, commit with
  `git -c user.name='SzaZo-Halycomp' -c user.email='dealer@ddsweb.hu' commit ...`.
- Only push when the user says so; they often test first.
- Match the surrounding code style: plain JS, `function` helpers, short comments
  explaining *why*, `log('[Area] ...')` logging.
