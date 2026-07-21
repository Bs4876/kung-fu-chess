# Kung-Fu Chess

Real-time chess variant where pieces move along the board over simulated time
instead of instantly, so multiple moves can be in flight at once. Played
over a real network: log in, then either get auto-matched by ELO or
create/join a room by a short code - with support for spectators,
disconnect/reconnect, and persistent ELO ratings.

This repository is split into:
- [`server/`](server/README.md) — the Python game engine, rules, and the
  WebSocket multiplayer server ([`server/net/`](server/net/README.md)).
- [`client/`](client/README.md) — the graphical client, built on the course-provided `Img` class.
