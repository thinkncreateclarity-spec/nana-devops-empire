#!/bin/bash
while true; do
  if ! pgrep -f "mpc-empire" > /dev/null; then
    echo "$(date): Restarting MPC Empire..."
    nohup bash ~/.termux/boot/mpc-empire > mpc-daemon.log 2>&1 &
  fi
  sleep 30
done
