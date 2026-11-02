# Dev/test helpers

None of these contain secrets: they read the HA URL and token from the app's own
`~/.config/ha-linux-companion/config.json` at run time (the panel must be logged in).
`ha_notify.py` refreshes an expired access token in memory with the stored refresh token
(the app only refreshes while it runs); it never writes to `config.json`.

| Tool | Use |
|---|---|
| `run-dev.sh [extra electron args]` | Start the app from the repo with the right Wayland/X11 env, detached; log to `/tmp/ha-companion-dev.log`. Stops a running instance first. |
| `ha_notify.py services` | List the HA `notify.mobile_app_*` services. |
| `ha_notify.py send <service> <msg>...` | Call `notify.<service>`. A msg may be `text::{json}` to add fields, e.g. `'command_volume_level::{"data":{"volume_level":0.3}}'`; `sleep2` pauses. |
| `cdp_eval.js '<js>'` | Evaluate JS in the running HA page (start the app with `--remote-debugging-address=127.0.0.1 --remote-debugging-port=9333`). Needs the repo's `node_modules/ws`. |
| `helper_test.js <fn,fn,...> '<js>'` | Pull top-level helper functions out of `src/main.js` and run them outside Electron, e.g. backlight/volume helpers against the real hardware. |
| `screenshot.sh [file]` | Full-screen screenshot on KDE Wayland via `spectacle`. |

Examples:

```bash
.claude/tools/run-dev.sh --remote-debugging-address=127.0.0.1 --remote-debugging-port=9333
python3 .claude/tools/ha_notify.py send mobile_app_test_classys command_screen_off sleep3 command_screen_on
node .claude/tools/cdp_eval.js 'window.__haLang + " " + location.pathname'
node .claude/tools/helper_test.js runShell,findBacklight,writeSysfs,getDisplayState 'console.log(findBacklight(), getDisplayState())'
```
