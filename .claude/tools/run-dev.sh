#!/bin/bash
# Start the app from this checkout, detached, the way run.sh from install.sh does.
# Extra args go to Electron, e.g. --remote-debugging-address=127.0.0.1 --remote-debugging-port=9333
# Uses --no-sandbox because chrome-sandbox in node_modules is not setuid root.
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
LOG="${HA_DEV_LOG:-/tmp/ha-companion-dev.log}"
export PATH="$HOME/.local/opt/node/bin:$PATH"

# Stop a running instance (Electron reorders argv, so match the binary path)
PIDS=$(ps -eo pid,args | grep '[e]lectron/dist/electron' | grep -v -- '--type=' | awk '{print $1}')
[ -n "$PIDS" ] && kill $PIDS && sleep 3

export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"
export DBUS_SESSION_BUS_ADDRESS="${DBUS_SESSION_BUS_ADDRESS:-unix:path=$XDG_RUNTIME_DIR/bus}"
if [ -z "$WAYLAND_DISPLAY" ] && [ -S "$XDG_RUNTIME_DIR/wayland-0" ]; then
  export WAYLAND_DISPLAY=wayland-0
fi
if [ -n "$WAYLAND_DISPLAY" ]; then
  export XDG_SESSION_TYPE=wayland
  unset DISPLAY
else
  export DISPLAY="${DISPLAY:-:0}"
fi

cd "$REPO"
if [ ! -x node_modules/electron/dist/electron ]; then
  echo "Electron missing: run 'npm install' and 'node node_modules/electron/install.js'" >&2
  exit 1
fi
setsid nohup ./node_modules/electron/dist/electron . --no-sandbox --ozone-platform-hint=auto "$@" > "$LOG" 2>&1 < /dev/null &
echo "started (log: $LOG)"
