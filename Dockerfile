# syntax=docker/dockerfile:1
# ============================================
# VERSION CUSTOM avec fork Aux-petits-Oignons
# Build du fork personnalisé avec config entreprise
# ============================================

# ============================================
# STAGE 1: BUILDER Python
# ============================================
FROM ubuntu:24.04 AS builder-python

ENV DEBIAN_FRONTEND=noninteractive

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    apt-get update && apt-get install -y \
    python3-pip python3-venv build-essential

WORKDIR /app
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    python3 -m venv venv && \
    . venv/bin/activate && \
    pip install -r requirements.txt markdown flask requests

# ============================================
# STAGE 2: CLONER le fork (sans build)
# ============================================
FROM alpine/git AS git-cloner

WORKDIR /build

# Cloner le fork Aux-petits-Oignons (on fera l'install au runtime)
RUN git clone https://github.com/PlumyCat/Aux-petits-Oignons.git .

# ============================================
# STAGE 3: RUNTIME
# ============================================
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# Packages système de base
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    apt-get update && apt-get install -y \
    python3 curl wget git rsync jq zip unzip \
    gnupg lsb-release software-properties-common apt-transport-https ca-certificates

# Azure CLI
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    curl -sL https://aka.ms/InstallAzureCLIDeb | bash

# .NET 8 SDK + Azure Functions Core Tools
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    wget -q https://packages.microsoft.com/config/ubuntu/24.04/packages-microsoft-prod.deb && \
    dpkg -i packages-microsoft-prod.deb && \
    rm packages-microsoft-prod.deb && \
    apt-get update && \
    apt-get install -y dotnet-sdk-8.0 azure-functions-core-tools-4

# Node.js (requis pour exécuter OpenCode)
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs

# Installer Bun (requis pour build et exécution OpenCode)
RUN curl -fsSL https://bun.sh/install | bash && \
    ln -s /root/.bun/bin/bun /usr/local/bin/bun

# Copier le fork cloné (non compilé) depuis git-cloner
COPY --from=git-cloner /build /opt/aux-petits-oignons

# Note: bun install + bun run build sera fait au démarrage dans entrypoint.sh

# Verify installations de base
RUN echo "=== Verification des installations ===" && \
    az --version | head -5 && \
    func --version && \
    bun --version

WORKDIR /app

# Copier le venv Python depuis builder
COPY --from=builder-python /app/venv /app/venv

# Configuration OpenCode - Préparer le répertoire (les fichiers seront copiés au runtime)
RUN mkdir -p /root/.config/opencode

# Copier les fichiers .env s'ils existent dans conf_opencode/
# Note: les fichiers de config du fork seront copiés au runtime par entrypoint.sh
RUN mkdir -p /tmp/conf_copy
COPY conf_opencode/ /tmp/conf_copy/
RUN if [ -f /tmp/conf_copy/.env ]; then \
        cp /tmp/conf_copy/.env /root/.config/opencode/.env; \
    elif [ -f /tmp/conf_copy/.env.example.custom ]; then \
        cp /tmp/conf_copy/.env.example.custom /root/.config/opencode/.env; \
    fi && \
    rm -rf /tmp/conf_copy

# Copy documentation server
COPY doc_server.py /app/doc_server.py

# Activate venv by default
ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Variables d'environnement pour le fork
ENV OPENCODE_ENTERPRISE_MODE=true
ENV OPENCODE_CONFIG_PATH=/root/.config/opencode/enterprise-config.json

# Message de bienvenue personnalisé
RUN echo '\n\
echo ""\n\
echo "========================================"\n\
echo "  🧅 Aux Petits Oignons - Be-Cloud"\n\
echo "========================================"\n\
echo ""\n\
echo "  Modeles IA disponibles (Azure):"\n\
echo "    - GPT-4.1 Mini    (defaut)"\n\
echo "    - GPT-5 Mini"\n\
echo "    - Model Routeur"\n\
echo "    - Claude Sonnet   (si disponible)"\n\
echo ""\n\
echo "  opencode      Nouvelle conversation"\n\
echo "  opencode -c   REPRENDRE conversation"\n\
echo ""\n\
echo "  az-update     Mettre a jour Azure CLI"\n\
echo ""\n\
echo "========================================"\n\
echo ""\n\
' >> /root/.bashrc

# Copy and setup entrypoint
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Empêcher OpenCode de détecter le fork comme projet
RUN mkdir -p /opt/aux-petits-oignons/.opencode && \
    echo '{"ignore": true}' > /opt/aux-petits-oignons/.opencode/config.json && \
    echo "**/*" > /opt/aux-petits-oignons/.opencodeignore && \
    touch /opt/aux-petits-oignons/.git/info/exclude && \
    echo "# OpenCode: Ce dossier n'est PAS un projet utilisateur" >> /opt/aux-petits-oignons/README.md

# Copier le guide de projet pour OpenCode
COPY CLAUDE-PROJET.md /app/CLAUDE.md

EXPOSE 8080

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["bash"]
