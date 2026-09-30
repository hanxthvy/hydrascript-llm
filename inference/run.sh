#!/usr/bin/env bash
# [xihanzu-NR]
set -e
CHAT_SCRIPT="/root/models/inference/chat_hydra.sh"
chmod +x "$CHAT_SCRIPT"

if [[ -n "$ZELLIJ" ]]; then
    exec "$CHAT_SCRIPT"
fi

exec zellij attach -c hxprjkt -- "$CHAT_SCRIPT"
