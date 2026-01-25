#!/bin/bash
# Wrapper pour lancer OpenCode avec les variables d'environnement

# Charger les variables depuis .env si le fichier existe
if [ -f /root/.config/opencode/.env ]; then
    set -a
    source /root/.config/opencode/.env 2>/dev/null
    set +a
fi

# Lancer OpenCode avec tous les arguments passés
exec opencode "$@"
