#!/bin/bash
set -e

# Alias pour mise à jour facile
echo 'alias az-update="az upgrade --yes"' >> /root/.bashrc

# Copy config files from mounted volume to config directory with correct permissions
if [ -d /app/conf_opencode_mount ]; then
    echo "Copying OpenCode configuration..."
    cp -f /app/conf_opencode_mount/opencode.json /root/.config/opencode/opencode.json 2>/dev/null || true

    # Copy .env if it exists, otherwise use .env.example
    if [ -f /app/conf_opencode_mount/.env ]; then
        cp -f /app/conf_opencode_mount/.env /root/.config/opencode/.env
    elif [ -f /app/conf_opencode_mount/.env.example ]; then
        cp -f /app/conf_opencode_mount/.env.example /root/.config/opencode/.env
    fi

    # Fix permissions
    chmod -R 755 /root/.config/opencode
    chmod 644 /root/.config/opencode/* 2>/dev/null || true
fi

# Execute the command
exec "$@"
