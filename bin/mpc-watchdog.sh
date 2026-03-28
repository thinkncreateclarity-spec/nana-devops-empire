#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

SERVICE_NAME="mpc-empire"
SERVICE_CMD="$HOME/.termux/boot/mpc-empire"
LOG_DIR="$HOME/nana-devops-empire"
LOG_FILE="$LOG_DIR/mpc-daemon.log"
INTERVAL=30               # seconds between checks
MAX_RESTARTS=5            # max restarts within WINDOW before giving up
WINDOW_SECONDS=300        # 5-minute rolling window

mkdir -p "$LOG_DIR"

restart_count=0
window_start=$(date +%s)

log() {
	printf '%s: %s\n' "$(date)" "$1" | tee -a "$LOG_FILE"
}

while true; do
  now=$(date +%s)
  # Reset window if enough time has passed
  if (( now - window_start > WINDOW_SECONDS )); then
    window_start=$now
    restart_count=0
  fi

  if ! pgrep -f "$SERVICE_NAME" > /dev/null 2>&1; then
    if (( restart_count >= MAX_RESTARTS )); then
      log "ERROR: $SERVICE_NAME down, restart limit reached (${MAX_RESTARTS}/${WINDOW_SECONDS}s). Not restarting further."
      sleep "$INTERVAL"
      continue
    fi

    log "WARN: $SERVICE_NAME not running. Restarting (attempt $((restart_count+1))/${MAX_RESTARTS})..."
    nohup bash "$SERVICE_CMD" >> "$LOG_FILE" 2>&1 &
    restart_count=$((restart_count+1))
  fi

  sleep "$INTERVAL"
done
