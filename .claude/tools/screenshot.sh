#!/bin/bash
# Full-screen screenshot on KDE Plasma (Wayland or X11) without UI.
OUT="${1:-/tmp/ha-companion-shot.png}"
export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"
export DBUS_SESSION_BUS_ADDRESS="${DBUS_SESSION_BUS_ADDRESS:-unix:path=$XDG_RUNTIME_DIR/bus}"
[ -z "$WAYLAND_DISPLAY" ] && [ -S "$XDG_RUNTIME_DIR/wayland-0" ] && export WAYLAND_DISPLAY=wayland-0
timeout 20 spectacle -b -n -f -o "$OUT" 2>/dev/null && echo "$OUT"
