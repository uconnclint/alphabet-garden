#!/bin/bash
# start-garden.command — double-click this to play Alphabet Garden.
# The game must be SERVED, not opened straight from the folder: browsers block ES modules
# over file://, which leaves the world blank. This serves the folder and opens the browser.
cd "$(dirname "$0")" || exit 1
PORT=8000
while lsof -i :$PORT >/dev/null 2>&1; do PORT=$((PORT+1)); done
echo "🌱 Alphabet Garden is starting on http://localhost:$PORT"
echo "   Leave this window open while you play. Close it to stop."
( sleep 1; open "http://localhost:$PORT" ) &
python3 -m http.server "$PORT"
