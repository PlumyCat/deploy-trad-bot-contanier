# Script de validation pre-build pour l'installeur Inno Setup
# STORY-001: Créer Installeur Windows .exe avec Inno Setup
# Vérifie que tous les fichiers référencés dans setup.iss existent

$ErrorActionPreference = "Stop"

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "Validation Pre-Build - Aux Petits Oignons" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

$Missing = 0
$Total = 0

function Check-File {
    param(
        [string]$Path,
        [string]$Description
    )

    $script:Total++
    $FullPath = Join-Path ".." $Path

    if (Test-Path $FullPath -PathType Leaf) {
        Write-Host "✓ " -ForegroundColor Green -NoNewline
        Write-Host $Description
        Write-Host "  → $Path"
    } else {
        Write-Host "✗ " -ForegroundColor Red -NoNewline
        Write-Host $Description
        Write-Host "  → $Path (MISSING)" -ForegroundColor Red
        $script:Missing++
    }
}

function Check-Dir {
    param(
        [string]$Path,
        [string]$Description
    )

    $script:Total++
    $FullPath = Join-Path ".." $Path

    if (Test-Path $FullPath -PathType Container) {
        Write-Host "✓ " -ForegroundColor Green -NoNewline
        Write-Host $Description
        Write-Host "  → $Path/"
    } else {
        Write-Host "✗ " -ForegroundColor Red -NoNewline
        Write-Host $Description
        Write-Host "  → $Path/ (MISSING)" -ForegroundColor Red
        $script:Missing++
    }
}

Write-Host "Checking Configuration Files..." -ForegroundColor Yellow
Write-Host "----------------------------------------"
Check-File "conf_opencode\opencode.json" "OpenCode configuration"
Check-File "conf_opencode\.env.example" "Environment template"
Write-Host ""

Write-Host "Checking Scripts..." -ForegroundColor Yellow
Write-Host "----------------------------------------"
Check-Dir "scripts" "Scripts directory"
Check-File "scripts\decrypt-credentials.ps1" "Decrypt credentials script"
Check-File "scripts\encrypt-credentials.ps1" "Encrypt credentials script"
Write-Host ""

Write-Host "Checking Core Files..." -ForegroundColor Yellow
Write-Host "----------------------------------------"
Check-File "Dockerfile" "Docker container definition"
Check-File "docker-compose.yml" "Docker Compose config"
Check-File "doc_server.py" "Flask documentation server"
Check-File "requirements.txt" "Python dependencies"
Check-File "entrypoint.sh" "Container entry point"
Write-Host ""

Write-Host "Checking Launcher Scripts..." -ForegroundColor Yellow
Write-Host "----------------------------------------"
Check-File "start.bat" "Main launcher (Windows)"
Check-File "configure.bat" "Configuration script (Windows)"
Check-File "repo-config.txt" "Repository configuration"
Write-Host ""

Write-Host "Checking Assets..." -ForegroundColor Yellow
Write-Host "----------------------------------------"
Check-File "icone\oignon.ico" "Application icon"
Write-Host ""

Write-Host "Checking Installer Files..." -ForegroundColor Yellow
Write-Host "----------------------------------------"
Check-File "installer\setup.iss" "Inno Setup script"
Check-File "installer\README.md" "Installer documentation"
Write-Host ""

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "Validation Summary" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Total files checked: $Total"
Write-Host "Missing files: " -NoNewline
Write-Host $Missing -ForegroundColor $(if ($Missing -eq 0) { "Green" } else { "Red" })
Write-Host ""

if ($Missing -eq 0) {
    Write-Host "✓ All files present!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Ready to compile installer with Inno Setup." -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Compile commands:" -ForegroundColor Yellow
    Write-Host "  GUI: Open setup.iss in Inno Setup Compiler and press Ctrl+F9"
    Write-Host "  CLI: `"C:\Program Files (x86)\Inno Setup 6\ISCC.exe`" setup.iss"
    Write-Host ""
    Write-Host "Output: installer\output\AuxPetitsOignons_Setup.exe" -ForegroundColor Cyan
    Write-Host ""
    exit 0
} else {
    Write-Host "✗ Missing $Missing file(s)!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please ensure all required files are present before compiling." -ForegroundColor Yellow
    Write-Host ""
    exit 1
}
