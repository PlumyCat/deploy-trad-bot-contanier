#!/bin/bash
set -e

# Clone or update source code from GitHub
REPO_URL="${REPO_URL:-https://github.com/PlumyCat/trad-bot-src.git}"
REPO_BRANCH="${REPO_BRANCH:-main}"

if [ ! -d "/app/src/.git" ]; then
    echo "Cloning source code from $REPO_URL..."

    # Clone to a temporary directory first
    git clone --branch "$REPO_BRANCH" --single-branch "$REPO_URL" /tmp/src_temp

    # Create /app/src and move .git
    mkdir -p /app/src
    mv /tmp/src_temp/.git /app/src/

    # Copy files that are NOT mounted as volumes (everything except clients/ and Solution/)
    rsync -av --exclude='clients/' --exclude='Solution/' /tmp/src_temp/ /app/src/

    # Copy clients/ and Solution/ content to the mounted volumes (from temp to /app/src/)
    if [ -d "/tmp/src_temp/clients" ]; then
        cp -rn /tmp/src_temp/clients/* /app/src/clients/ 2>/dev/null || true
    fi
    if [ -d "/tmp/src_temp/Solution" ]; then
        cp -rn /tmp/src_temp/Solution/* /app/src/Solution/ 2>/dev/null || true
    fi

    rm -rf /tmp/src_temp
    echo "Source code cloned successfully"
else
    echo "Updating source code..."
    cd /app/src
    git fetch origin "$REPO_BRANCH" 2>/dev/null || true
    LOCAL_HASH=$(git rev-parse HEAD 2>/dev/null || echo "")
    REMOTE_HASH=$(git rev-parse origin/"$REPO_BRANCH" 2>/dev/null || echo "")

    if [ "$LOCAL_HASH" != "$REMOTE_HASH" ] && [ -n "$REMOTE_HASH" ]; then
        echo "New version available, updating..."
        git pull origin "$REPO_BRANCH" || echo "Update failed, using local version"

        # Update clients/ and Solution/ if they have new files (without overwriting user data)
        if [ -d ".git" ]; then
            cd /app/src
            # Copy new files from repo to volumes (without overwriting existing)
            find clients/ -type f 2>/dev/null | while read f; do
                [ ! -f "$f" ] && git checkout HEAD -- "$f" 2>/dev/null || true
            done
            find Solution/ -type f 2>/dev/null | while read f; do
                [ ! -f "$f" ] && git checkout HEAD -- "$f" 2>/dev/null || true
            done
        fi
    else
        echo "Source code already up to date"
    fi
    cd /app
fi

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
