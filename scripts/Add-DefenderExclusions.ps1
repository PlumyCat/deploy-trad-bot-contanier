#Requires -RunAsAdministrator
<#
.SYNOPSIS
    Crée les exclusions Windows Defender ASR pour "Aux Petits Oignons"

.DESCRIPTION
    Ce script crée des exclusions ciblées Windows Defender pour permettre l'exécution
    de l'installeur non-signé "Aux Petits Oignons" et de ses composants Docker.

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
    .\Add-DefenderExclusions.ps1
    Crée les exclusions avec les chemins par défaut

.EXAMPLE
    .\Add-DefenderExclusions.ps1 -Quiet
    Crée les exclusions sans demander de confirmation

.EXAMPLE
    .\Add-DefenderExclusions.ps1 -InstallPath "D:\AuxPetitsOignons"
    Crée les exclusions avec un chemin d'installation personnalisé

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

# Fonction pour vérifier si Defender est actif
function Test-DefenderActive {
    try {
        $status = Get-MpComputerStatus -ErrorAction SilentlyContinue
        return ($status -ne $null -and $status.AntivirusEnabled -eq $true)
    } catch {
        return $false
    }
}

# Fonction pour ajouter une exclusion de chemin
function Add-PathExclusion {
    param(
        [string]$Path,
        [string]$Description
    )

    try {
        # Vérifier si l'exclusion existe déjà
        $existingExclusions = (Get-MpPreference).ExclusionPath
        if ($existingExclusions -contains $Path) {
            Write-Info "$Description : Déjà exclu"
            return $true
        }

        # Ajouter l'exclusion
        Add-MpPreference -ExclusionPath $Path -ErrorAction Stop
        Write-Success "$Description : Exclusion ajoutée"
        return $true
    } catch {
        Write-Error "$Description : Échec - $($_.Exception.Message)"
        return $false
    }
}

# Fonction pour ajouter une exclusion de processus
function Add-ProcessExclusion {
    param(
        [string]$ProcessName,
        [string]$Description
    )

    try {
        # Vérifier si l'exclusion existe déjà
        $existingExclusions = (Get-MpPreference).ExclusionProcess
        if ($existingExclusions -contains $ProcessName) {
            Write-Info "$Description : Déjà exclu"
            return $true
        }

        # Ajouter l'exclusion
        Add-MpPreference -ExclusionProcess $ProcessName -ErrorAction Stop
        Write-Success "$Description : Exclusion ajoutée"
        return $true
    } catch {
        Write-Error "$Description : Échec - $($_.Exception.Message)"
        return $false
    }
}

# ========================================
# MAIN SCRIPT
# ========================================

try {
    Write-Header "Exclusions Defender ASR - Aux Petits Oignons"

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

    # 2. Vérifier que Defender est actif
    Write-Info "Vérification Windows Defender..."
    if (-not (Test-DefenderActive)) {
        Write-Warning "Windows Defender ne semble pas actif sur ce système."
        Write-Warning "Les exclusions ne sont pas nécessaires si Defender est désactivé."

        if (-not $Quiet) {
            $continue = Read-Host "Voulez-vous continuer quand même? (O/N)"
            if ($continue -ne "O" -and $continue -ne "o") {
                Write-Info "Opération annulée par l'utilisateur."
                exit 0
            }
        }
    } else {
        Write-Success "Windows Defender est actif"
    }

    # 3. Afficher les chemins cibles
    Write-Host ""
    Write-Info "Chemins à exclure:"
    Write-Host "  Installation:    $InstallPath"
    Write-Host "  Données:         $DataPath"
    Write-Host "  OpenCode:        $env:USERPROFILE\.opencode"
    Write-Host "  LocalAppData:    $env:LOCALAPPDATA\Programs\AuxPetitsOignons"
    Write-Host "  AppData:         $env:USERPROFILE\AppData\AuxPetitsOignons"
    Write-Host ""
    Write-Info "Processus à exclure:"
    Write-Host "  - docker.exe"
    Write-Host "  - dockerd.exe"
    Write-Host "  - com.docker.backend.exe"
    Write-Host ""

    # 4. Demander confirmation (sauf si -Quiet)
    if (-not $Quiet) {
        Write-Warning "ATTENTION: Ces exclusions permettront l'exécution de fichiers non-signés."
        Write-Warning "Assurez-vous de faire confiance à la source 'Aux Petits Oignons'."
        Write-Host ""
        $confirm = Read-Host "Voulez-vous créer ces exclusions? (O/N)"
        if ($confirm -ne "O" -and $confirm -ne "o") {
            Write-Info "Opération annulée par l'utilisateur."
            exit 0
        }
    }

    Write-Host ""
    Write-Header "Création des Exclusions"

    # 5. Créer les exclusions de chemins
    $pathExclusions = @(
        @{Path = $InstallPath; Description = "Installation principale"},
        @{Path = $DataPath; Description = "Dossier de données"},
        @{Path = "$env:LOCALAPPDATA\Programs\AuxPetitsOignons"; Description = "LocalAppData"},
        @{Path = "$env:USERPROFILE\AppData\AuxPetitsOignons"; Description = "AppData"},
        @{Path = "$env:USERPROFILE\.opencode"; Description = "Configuration OpenCode"}
    )

    $successCount = 0
    $totalCount = $pathExclusions.Count

    Write-Info "Ajout des exclusions de chemins..."
    foreach ($exclusion in $pathExclusions) {
        if (Add-PathExclusion -Path $exclusion.Path -Description $exclusion.Description) {
            $successCount++
        }
    }

    Write-Host ""

    # 6. Créer les exclusions de processus Docker
    $processExclusions = @(
        @{Process = "docker.exe"; Description = "Docker CLI"},
        @{Process = "dockerd.exe"; Description = "Docker Daemon"},
        @{Process = "com.docker.backend.exe"; Description = "Docker Backend"}
    )

    $processSuccessCount = 0
    $processTotalCount = $processExclusions.Count

    Write-Info "Ajout des exclusions de processus..."
    foreach ($exclusion in $processExclusions) {
        if (Add-ProcessExclusion -ProcessName $exclusion.Process -Description $exclusion.Description) {
            $processSuccessCount++
        }
    }

    # 7. Résumé
    Write-Host ""
    Write-Header "Résumé"

    $totalSuccess = $successCount + $processSuccessCount
    $grandTotal = $totalCount + $processTotalCount

    Write-Host "Exclusions de chemins:   $successCount/$totalCount créées"
    Write-Host "Exclusions de processus: $processSuccessCount/$processTotalCount créées"
    Write-Host "Total:                   $totalSuccess/$grandTotal créées"
    Write-Host ""

    if ($totalSuccess -eq $grandTotal) {
        Write-Success "Toutes les exclusions ont été créées avec succès!"
        Write-Host ""
        Write-Info "Vous pouvez maintenant installer 'Aux Petits Oignons' sans blocage Defender."
        exit 0
    } elseif ($totalSuccess -gt 0) {
        Write-Warning "Certaines exclusions n'ont pas pu être créées."
        Write-Warning "Vérifiez les messages d'erreur ci-dessus."
        exit 2
    } else {
        Write-Error "Aucune exclusion n'a pu être créée."
        Write-Error "Vérifiez les permissions et la configuration de Defender."
        exit 1
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
