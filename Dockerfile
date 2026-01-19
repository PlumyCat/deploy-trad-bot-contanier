# ============================================
# STAGE 1: BUILDER (avec pip pour construire venv)
# ============================================
FROM ubuntu:24.04 AS builder

ENV DEBIAN_FRONTEND=noninteractive

# Installation Python et outils de build (uniquement pour builder)
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-venv \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Créer le venv et installer les dépendances Python
WORKDIR /app
COPY requirements.txt .
RUN python3 -m venv venv && \
    . venv/bin/activate && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir markdown flask requests && \
    pip cache purge

# ============================================
# STAGE 2: RUNTIME (image finale optimisée)
# ============================================
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# ============================================
# Installation CONSOLIDÉE de TOUS les packages
# ============================================
RUN apt-get update && apt-get install -y \
    # Python runtime (PAS build-essential)
    python3 \
    # Outils système
    curl wget git rsync jq zip unzip \
    # Pour repositories externes
    gnupg lsb-release software-properties-common apt-transport-https ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# ============================================
# Azure CLI (installation + nettoyage)
# ============================================
RUN curl -sL https://aka.ms/InstallAzureCLIDeb | bash && \
    rm -rf /var/lib/apt/lists/*

# ============================================
# .NET 8 SDK (requis par Azure Functions Core Tools)
# ============================================
RUN wget -q https://packages.microsoft.com/config/ubuntu/24.04/packages-microsoft-prod.deb && \
    dpkg -i packages-microsoft-prod.deb && \
    rm packages-microsoft-prod.deb && \
    apt-get update && \
    apt-get install -y dotnet-sdk-8.0 && \
    rm -rf /var/lib/apt/lists/*

# ============================================
# Azure Functions Core Tools v4
# CRITIQUE: C'est le plus long, mais NÉCESSAIRE
# ============================================
RUN apt-get update && \
    apt-get install -y azure-functions-core-tools-4 && \
    rm -rf /var/lib/apt/lists/*

# ============================================
# Node.js + OpenCode (installation + nettoyage agressif)
# ============================================
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g opencode-ai@latest && \
    npm cache clean --force && \
    rm -rf ~/.npm /tmp/npm* /var/lib/apt/lists/*

# Verify installations
RUN echo "=== Verification des installations ===" && \
    az --version | head -5 && \
    func --version && \
    which opencode && opencode --version

WORKDIR /app

# ============================================
# Copier le venv depuis le builder (économise espace)
# ============================================
COPY --from=builder /app/venv /app/venv

# ============================================
# Configuration OpenCode
# ============================================
RUN mkdir -p /root/.config/opencode

COPY conf_opencode/opencode.json /root/.config/opencode/
COPY conf_opencode/.env* /root/.config/opencode/
RUN if [ ! -f /root/.config/opencode/.env ]; then \
    cp /root/.config/opencode/.env.example /root/.config/opencode/.env 2>/dev/null || true; \
    fi

# Copy documentation server
COPY doc_server.py /app/doc_server.py

# Activate venv by default
ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# ============================================
# Message de bienvenue
# ============================================
RUN echo '\n\
echo ""\n\
echo "========================================"\n\
echo "  🧅 Aux Petits Oignons - Be-Cloud"\n\
echo "========================================"\n\
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

# Copy OpenCode wrapper (removed from Dockerfile, using entrypoint function instead)

# Expose port for documentation server
EXPOSE 8080

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["bash"]
