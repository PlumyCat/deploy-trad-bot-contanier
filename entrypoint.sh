#!/bin/bash
set -e

# ============================================
# Build OpenCode Fork (au premier démarrage)
# ============================================
if [ ! -f "/opt/aux-petits-oignons/.build_done" ]; then
    echo "=========================================="
    echo "  Premier démarrage - Compilation du fork"
    echo "  Aux Petits Oignons (OpenCode custom)"
    echo "=========================================="
    echo ""

    cd /opt/aux-petits-oignons

    echo "Installation des dépendances Bun..."
    if bun install; then
        echo "✓ Dépendances installées"

        # Mettre à jour baseline-browser-mapping pour supprimer le warning obsolète
        echo "Mise à jour baseline-browser-mapping..."
        cd /opt/aux-petits-oignons/packages/opencode
        bun update baseline-browser-mapping 2>/dev/null || true
        cd /opt/aux-petits-oignons

        echo ""
        echo "Configuration du fork OpenCode..."

        # Créer un wrapper bash pour lancer OpenCode avec Bun
        cat > /usr/local/bin/opencode <<'OPENCODE_WRAPPER'
#!/bin/bash
# Wrapper pour lancer le fork Aux-petits-Oignons avec Bun
# Force le projet à être le répertoire courant
WORK_DIR="$(pwd)"

# Créer marqueur de projet OpenCode si pas déjà présent
if [ ! -f "$WORK_DIR/.opencode/project.json" ]; then
    mkdir -p "$WORK_DIR/.opencode"
    echo '{"name":"trad-bot-src","root":"'$WORK_DIR'"}' > "$WORK_DIR/.opencode/project.json"
fi

# Lancer OpenCode depuis le répertoire de travail
cd "$WORK_DIR"
exec bun --conditions=browser /opt/aux-petits-oignons/packages/opencode/src/index.ts "$@"
OPENCODE_WRAPPER
        chmod +x /usr/local/bin/opencode

        # Copier les fichiers de configuration entreprise
        mkdir -p /root/.config/opencode

        if [ -f /opt/aux-petits-oignons/config/enterprise-config.json ]; then
            cp /opt/aux-petits-oignons/config/enterprise-config.json /root/.config/opencode/
        fi

        if [ -f /opt/aux-petits-oignons/.opencode/opencode.jsonc ]; then
            cp /opt/aux-petits-oignons/.opencode/opencode.jsonc /root/.config/opencode/opencode.json
        fi

        if [ -f /opt/aux-petits-oignons/.env.example ]; then
            cp /opt/aux-petits-oignons/.env.example /root/.config/opencode/.env.example
        fi

        # Marquer comme configuré
        touch /opt/aux-petits-oignons/.build_done

        echo "✓ Fork OpenCode configuré"
        echo ""
        echo "=========================================="
        echo "  ✓ Fork Aux Petits Oignons prêt"
        echo "=========================================="
        echo ""
    else
        echo "✗ ERREUR lors de l'installation des dépendances"
        echo "Le container continuera sans OpenCode custom"
    fi

    cd /app
fi

# Load repo configuration from file if it exists
if [ -f "/app/repo-config.txt" ]; then
    echo "Loading repository configuration from repo-config.txt..."
    source /app/repo-config.txt
fi

# Clone or update source code from GitHub
REPO_URL="${REPO_URL:-https://github.com/PlumyCat/trad-bot-src.git}"
REPO_BRANCH="${REPO_BRANCH:-main}"

echo "Repository: $REPO_URL (branch: $REPO_BRANCH)"

if [ ! -d "/app/src/.git" ]; then
    echo "Cloning source code from $REPO_URL..."

    # Clone to a temporary directory first
    if git clone --branch "$REPO_BRANCH" --single-branch "$REPO_URL" /tmp/src_temp 2>/tmp/clone_error.log; then
        echo "Clone successful, setting up directory structure..."

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
        echo "✓ Source code cloned successfully"
    else
        echo "✗ ERROR: Failed to clone repository"
        echo "Repository URL: $REPO_URL"
        echo "Branch: $REPO_BRANCH"
        if [ -f /tmp/clone_error.log ]; then
            echo "Error details:"
            cat /tmp/clone_error.log
        fi
        echo ""
        echo "Possible causes:"
        echo "  - Network connectivity issue"
        echo "  - Invalid repository URL"
        echo "  - Branch does not exist"
        echo "  - Private repository requires authentication"
        echo ""
        echo "Container will continue without source code."
        echo "You can manually clone later or fix repo-config.txt and restart."
        mkdir -p /app/src
        rm -rf /tmp/src_temp /tmp/clone_error.log
    fi
else
    echo "Repository already exists, checking for updates..."
    cd /app/src

    if git fetch origin "$REPO_BRANCH" 2>/dev/null; then
        LOCAL_HASH=$(git rev-parse HEAD 2>/dev/null || echo "")
        REMOTE_HASH=$(git rev-parse origin/"$REPO_BRANCH" 2>/dev/null || echo "")

        if [ "$LOCAL_HASH" != "$REMOTE_HASH" ] && [ -n "$REMOTE_HASH" ]; then
            echo "New version available (local: ${LOCAL_HASH:0:7}, remote: ${REMOTE_HASH:0:7})"
            echo "Updating source code..."

            if git pull origin "$REPO_BRANCH" 2>/dev/null; then
                echo "✓ Source code updated successfully"

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
                echo "✗ Update failed, using local version (${LOCAL_HASH:0:7})"
            fi
        else
            echo "✓ Source code already up to date (${LOCAL_HASH:0:7})"
        fi
    else
        echo "⚠ Cannot fetch updates (network issue or invalid remote)"
        echo "Continuing with local version"
    fi
    cd /app
fi

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

    # Convert Windows line endings (CRLF) to Unix (LF) if needed
    if [ -f /root/.config/opencode/.env ]; then
        echo "Converting line endings..."
        tr -d '\r' < /root/.config/opencode/.env > /root/.config/opencode/.env.unix
        mv /root/.config/opencode/.env.unix /root/.config/opencode/.env
    fi
fi

# Alias pour mise à jour facile
echo 'alias az-update="az upgrade --yes"' >> /root/.bashrc

# Fonction pour opencode avec chargement automatique du .env
cat >> /root/.bashrc <<'BASHRC_EOF'
opencode() {
    set -a
    source /root/.config/opencode/.env 2>/dev/null
    set +a
    command opencode "$@"
}
BASHRC_EOF

# Execute the command
exec "$@"
