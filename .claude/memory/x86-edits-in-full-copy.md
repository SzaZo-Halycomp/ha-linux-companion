---
name: x86-edits-in-full-copy
description: "The user's original Intel/x64 + Docker X11 experiments in /srv/omnIQ/srv/full/ha-linux-companion; x86 parts are ported into the fork, Docker host-X11 variant is not"
metadata:
  node_type: memory
  type: project
  originSessionId: c96249c4-a94f-4c33-a490-37b3c933dd2a
  modified: 2026-11-02T12:54:51.525Z
---

`/srv/omnIQ/srv/full/ha-linux-companion` (upstream v2.5.0 clone) holds the user's uncommitted experiments:
`intel_backlight/bl_power` screen control, x64 build targets, and a Docker setup using the host X11 socket,
mutter xauth from /run/user/1000, uid 1000, network_mode host and a system dbus.

As of 2026-10-26 the x86 parts are implemented properly in the fork (`/srv/omnIQ/ha-linux-companion`,
commit 6bf4ea8 and later). The Docker host-X11 variant was **not** ported — use that copy as reference if
the user asks for Docker on x86.

See [[ha-companion-handoff]] for the full project state.
