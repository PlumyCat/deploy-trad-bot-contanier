# ============================================
# Aux Petits Oignons - Container Docker
# ============================================
# Container Ubuntu 24.04 pre-configure avec:
# - OpenCode (AI agent pour deploiement Azure)
# - Azure CLI (derniere version)
# - Azure Functions Core Tools v4
# - Flask (serveur documentation)
# - Python 3.11+ avec venv
#
# Objectifs:
# - Build < 5 minutes
# - Demarrage < 2 minutes
# - Taille < 2GB
#
# Story: STORY-003 (8 points)
# ============================================

FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-venv \
    curl \
    wget \
    git \
    rsync \
    gnupg \
    lsb-release \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    unzip \
    jq \
    zip \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# ============================================
# Install Azure CLI
# ============================================
RUN curl -sL https://aka.ms/InstallAzureCLIDeb | bash

# ============================================
# Install .NET 8 SDK (requis par Azure Functions)
# ============================================
RUN wget -q https://packages.microsoft.com/config/ubuntu/24.04/packages-microsoft-prod.deb && \
    dpkg -i packages-microsoft-prod.deb && \
    rm packages-microsoft-prod.deb && \
    apt-get update && \
    apt-get install -y dotnet-sdk-8.0 && \
    rm -rf /var/lib/apt/lists/*

# ============================================
# Install Azure Functions Core Tools v4
# ============================================
RUN apt-get update && \
    apt-get install -y azure-functions-core-tools-4 && \
    rm -rf /var/lib/apt/lists/*

# ============================================
# Install Node.js and OpenCode
# ============================================
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g opencode-ai@latest && \
    rm -rf /var/lib/apt/lists/*

# Verify installations
RUN echo "=== Verification des installations ===" && \
    az --version | head -5 && \
    func --version && \
    which opencode && opencode --version

WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN python3 -m venv venv && \
    . venv/bin/activate && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install markdown flask requests

# Create OpenCode config directory
RUN mkdir -p /root/.config/opencode

# Copy OpenCode configuration files
# Use .env if it exists, otherwise use .env.example as fallback
COPY conf_opencode/opencode.json /root/.config/opencode/
COPY conf_opencode/.env* /root/.config/opencode/
RUN if [ ! -f /root/.config/opencode/.env ]; then \
    cp /root/.config/opencode/.env.example /root/.config/opencode/.env 2>/dev/null || true; \
    fi

# Source code will be cloned from GitHub at runtime by entrypoint.sh

# Copy documentation server
COPY doc_server.py /app/doc_server.py

# Activate venv by default
ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Message de bienvenue dans le container
RUN echo '\n\
echo ""\n\
echo "========================================"\n\
echo "  🧅 Aux Petits Oignons"\n\
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

# Expose port for documentation server (Flask)
# Note: Mapped to 5545 externally via docker-compose.yml
# Access documentation at http://localhost:5545/procedure
EXPOSE 8080

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["bash"]
