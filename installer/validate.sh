#!/bin/bash
# Script de validation pre-build pour l'installeur Inno Setup
# STORY-001: Créer Installeur Windows .exe avec Inno Setup
# Vérifie que tous les fichiers référencés dans setup.iss existent

set -e

echo "=================================================="
echo "Validation Pre-Build - Aux Petits Oignons"
echo "=================================================="
echo ""

# Couleurs pour output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

MISSING=0
TOTAL=0

# Fonction de vérification
check_file() {
    local file="$1"
    local description="$2"
    TOTAL=$((TOTAL + 1))

    if [ -f "../$file" ]; then
        echo -e "${GREEN}✓${NC} $description"
        echo "  → $file"
    else
        echo -e "${RED}✗${NC} $description"
        echo "  → $file (MISSING)"
        MISSING=$((MISSING + 1))
    fi
}

check_dir() {
    local dir="$1"
    local description="$2"
    TOTAL=$((TOTAL + 1))

    if [ -d "../$dir" ]; then
        echo -e "${GREEN}✓${NC} $description"
        echo "  → $dir/"
    else
        echo -e "${RED}✗${NC} $description"
        echo "  → $dir/ (MISSING)"
        MISSING=$((MISSING + 1))
    fi
}

echo "Checking Configuration Files..."
echo "----------------------------------------"
check_file "conf_opencode/opencode.json" "OpenCode configuration"
check_file "conf_opencode/.env.example" "Environment template"
echo ""

echo "Checking Scripts..."
echo "----------------------------------------"
check_dir "scripts" "Scripts directory"
check_file "scripts/decrypt-credentials.ps1" "Decrypt credentials script"
check_file "scripts/encrypt-credentials.ps1" "Encrypt credentials script"
echo ""

echo "Checking Core Files..."
echo "----------------------------------------"
check_file "Dockerfile" "Docker container definition"
check_file "docker-compose.yml" "Docker Compose config"
check_file "doc_server.py" "Flask documentation server"
check_file "requirements.txt" "Python dependencies"
check_file "entrypoint.sh" "Container entry point"
echo ""

echo "Checking Launcher Scripts..."
echo "----------------------------------------"
check_file "start.bat" "Main launcher (Windows)"
check_file "configure.bat" "Configuration script (Windows)"
check_file "repo-config.txt" "Repository configuration"
echo ""

echo "Checking Assets..."
echo "----------------------------------------"
check_file "icone/oignon.ico" "Application icon"
echo ""

echo "Checking Installer Files..."
echo "----------------------------------------"
check_file "installer/setup.iss" "Inno Setup script"
check_file "installer/README.md" "Installer documentation"
echo ""

echo "=================================================="
echo "Validation Summary"
echo "=================================================="
echo ""
echo "Total files checked: $TOTAL"
echo -e "Missing files: ${RED}$MISSING${NC}"
echo ""

if [ $MISSING -eq 0 ]; then
    echo -e "${GREEN}✓ All files present!${NC}"
    echo ""
    echo "Ready to compile installer with Inno Setup on Windows."
    echo "Run: \"C:\\Program Files (x86)\\Inno Setup 6\\ISCC.exe\" setup.iss"
    echo ""
    exit 0
else
    echo -e "${RED}✗ Missing $MISSING file(s)!${NC}"
    echo ""
    echo "Please ensure all required files are present before compiling."
    echo ""
    exit 1
fi
