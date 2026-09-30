#!/usr/bin/env bash
# [xihanzu-NR]
set -e
CHAT_SCRIPT="/root/models/inference/chat_hydra.sh"
chmod +x "$CHAT_SCRIPT"

# If already inside a Zellij session, run directly
if [[ -n "$ZELLIJ" ]]; then
    exec "$CHAT_SCRIPT" "$@"
fi

# Clean up any dead/exited session named hxprjkt
if zellij list-sessions 2>/dev/null | grep -qE "hxprjkt.*(EXITED|DEAD)"; then
    zellij delete-session --force hxprjkt 2>/dev/null || true
fi

# Launch or attach to hxprjkt session with automatic cleanup when chat exits
exec zellij attach -c --close-on-exit hxprjkt -- "$CHAT_SCRIPT" "$@"
