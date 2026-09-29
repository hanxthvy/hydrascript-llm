#!/usr/bin/env bash
# [xihanzu-NR]
set -e

CHAT_SCRIPT="/root/models/chat_hydra.sh"

# Pastikan script chat executable
chmod +x "$CHAT_SCRIPT"

# Jika sudah di dalam zellij, jalankan chat langsung
if [[ -n "$ZELLIJ" ]]; then
    exec "$CHAT_SCRIPT"
fi

# Jika di luar zellij, buat/attach sesi zellij 'hxprjkt'
exec zellij attach -c hxprjkt -- "$CHAT_SCRIPT"
