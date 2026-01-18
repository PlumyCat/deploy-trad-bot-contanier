#Requires -RunAsAdministrator
<#
.SYNOPSIS
    Supprime les exclusions Windows Defender ASR pour "Aux Petits Oignons"

.DESCRIPTION
    Ce script supprime les exclusions Windows Defender créées par Add-DefenderExclusions.ps1
    Utilisé lors de la désinstallation ou pour annuler les exclusions.

    IMPORTANT: Ce script nécessite des droits administrateur.

    Story: STORY-002 - Script PowerShell Exclusions Defender ASR
    Version: 1.0
    Date: 2026-01-18

.PARAMETER InstallPath
    Chemin d'installation personnalisé (par défaut: C:\Program Files\AuxPetitsOignons)

.PARAMETER DataPath
    Chemin des données personnalisé (par défaut: %USERPROFILE%\AuxPetitsOignons)

.PARAMETER Quiet
    Mode silencieux (pas de confirmation utilisateur)

.EXAMPLE
    .\Remove-DefenderExclusions.ps1
    Supprime les exclusions avec les chemins par défaut

.EXAMPLE
    .\Remove-DefenderExclusions.ps1 -Quiet
    Supprime les exclusions sans demander de confirmation

.NOTES
    Auteur: Eric (Be-Cloud)
    Nécessite: Windows 10/11 avec Windows Defender activé
    Nécessite: Droits administrateur
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [string]$InstallPath = "$env:ProgramFiles\AuxPetitsOignons",

    [Parameter(Mandatory=$false)]
    [string]$DataPath = "$env:USERPROFILE\AuxPetitsOignons",

    [Parameter(Mandatory=$false)]
    [switch]$Quiet
)

# Configuration
$ErrorActionPreference = "Stop"
$WarningPreference = "Continue"

# Couleurs pour output
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Write-Header {
    param([string]$Title)
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host $Title -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Success {
    param([string]$Message)
    Write-ColorOutput "✓ $Message" "Green"
}

function Write-Error {
    param([string]$Message)
    Write-ColorOutput "✗ $Message" "Red"
}

function Write-Info {
    param([string]$Message)
    Write-ColorOutput "ℹ $Message" "Cyan"
}

function Write-Warning {
    param([string]$Message)
    Write-ColorOutput "⚠ $Message" "Yellow"
}

# Fonction de vérification des droits administrateur
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Fonction pour supprimer une exclusion de chemin
function Remove-PathExclusion {
    param(
        [string]$Path,
        [string]$Description
    )

    try {
        # Vérifier si l'exclusion existe
        $existingExclusions = (Get-MpPreference).ExclusionPath
        if ($existingExclusions -notcontains $Path) {
            Write-Info "$Description : Déjà absent"
            return $true
        }

        # Supprimer l'exclusion
        Remove-MpPreference -ExclusionPath $Path -ErrorAction Stop
        Write-Success "$Description : Exclusion supprimée"
        return $true
    } catch {
        Write-Warning "$Description : Impossible de supprimer - $($_.Exception.Message)"
        return $false
    }
}

# Fonction pour supprimer une exclusion de processus
function Remove-ProcessExclusion {
    param(
        [string]$ProcessName,
        [string]$Description
    )

    try {
        # Vérifier si l'exclusion existe
        $existingExclusions = (Get-MpPreference).ExclusionProcess
        if ($existingExclusions -notcontains $ProcessName) {
            Write-Info "$Description : Déjà absent"
            return $true
        }

        # Supprimer l'exclusion
        Remove-MpPreference -ExclusionProcess $ProcessName -ErrorAction Stop
        Write-Success "$Description : Exclusion supprimée"
        return $true
    } catch {
        Write-Warning "$Description : Impossible de supprimer - $($_.Exception.Message)"
        return $false
    }
}

# ========================================
# MAIN SCRIPT
# ========================================

try {
    Write-Header "Suppression Exclusions Defender - Aux Petits Oignons"

    # 1. Vérifier les droits administrateur
    Write-Info "Vérification des droits administrateur..."
    if (-not (Test-Administrator)) {
        Write-Error "Ce script nécessite des droits administrateur."
        Write-Host ""
        Write-Host "Veuillez relancer PowerShell en tant qu'administrateur:" -ForegroundColor Yellow
        Write-Host "  1. Clic droit sur PowerShell" -ForegroundColor Yellow
        Write-Host "  2. Sélectionner 'Exécuter en tant qu'administrateur'" -ForegroundColor Yellow
        Write-Host ""
        exit 1
    }
    Write-Success "Droits administrateur confirmés"

    # 2. Afficher les chemins cibles
    Write-Host ""
    Write-Info "Exclusions à supprimer:"
    Write-Host "  Installation:    $InstallPath"
    Write-Host "  Données:         $DataPath"
    Write-Host "  OpenCode:        $env:USERPROFILE\.opencode"
    Write-Host "  LocalAppData:    $env:LOCALAPPDATA\Programs\AuxPetitsOignons"
    Write-Host "  AppData:         $env:USERPROFILE\AppData\AuxPetitsOignons"
    Write-Host ""
    Write-Host "  Processus:       docker.exe, dockerd.exe, com.docker.backend.exe"
    Write-Host ""

    # 3. Demander confirmation (sauf si -Quiet)
    if (-not $Quiet) {
        $confirm = Read-Host "Voulez-vous supprimer ces exclusions? (O/N)"
        if ($confirm -ne "O" -and $confirm -ne "o") {
            Write-Info "Opération annulée par l'utilisateur."
            exit 0
        }
    }

    Write-Host ""
    Write-Header "Suppression des Exclusions"

    # 4. Supprimer les exclusions de chemins
    $pathExclusions = @(
        @{Path = $InstallPath; Description = "Installation principale"},
        @{Path = $DataPath; Description = "Dossier de données"},
        @{Path = "$env:LOCALAPPDATA\Programs\AuxPetitsOignons"; Description = "LocalAppData"},
        @{Path = "$env:USERPROFILE\AppData\AuxPetitsOignons"; Description = "AppData"},
        @{Path = "$env:USERPROFILE\.opencode"; Description = "Configuration OpenCode"}
    )

    $successCount = 0
    $totalCount = $pathExclusions.Count

    Write-Info "Suppression des exclusions de chemins..."
    foreach ($exclusion in $pathExclusions) {
        if (Remove-PathExclusion -Path $exclusion.Path -Description $exclusion.Description) {
            $successCount++
        }
    }

    Write-Host ""

    # 5. Supprimer les exclusions de processus Docker
    $processExclusions = @(
        @{Process = "docker.exe"; Description = "Docker CLI"},
        @{Process = "dockerd.exe"; Description = "Docker Daemon"},
        @{Process = "com.docker.backend.exe"; Description = "Docker Backend"}
    )

    $processSuccessCount = 0
    $processTotalCount = $processExclusions.Count

    Write-Info "Suppression des exclusions de processus..."
    foreach ($exclusion in $processExclusions) {
        if (Remove-ProcessExclusion -ProcessName $exclusion.Process -Description $exclusion.Description) {
            $processSuccessCount++
        }
    }

    # 6. Résumé
    Write-Host ""
    Write-Header "Résumé"

    $totalSuccess = $successCount + $processSuccessCount
    $grandTotal = $totalCount + $processTotalCount

    Write-Host "Exclusions de chemins:   $successCount/$totalCount supprimées"
    Write-Host "Exclusions de processus: $processSuccessCount/$processTotalCount supprimées"
    Write-Host "Total:                   $totalSuccess/$grandTotal supprimées"
    Write-Host ""

    if ($totalSuccess -eq $grandTotal) {
        Write-Success "Toutes les exclusions ont été supprimées avec succès!"
        Write-Host ""
        Write-Info "Windows Defender reprendra la protection normale de ces chemins."
        exit 0
    } else {
        Write-Warning "Certaines exclusions n'ont pas pu être supprimées (probablement déjà absentes)."
        exit 0
    }

} catch {
    Write-Host ""
    Write-Error "Erreur inattendue: $($_.Exception.Message)"
    Write-Host ""
    Write-Host "Stack trace:" -ForegroundColor Gray
    Write-Host $_.ScriptStackTrace -ForegroundColor Gray
    Write-Host ""
    exit 99
}
