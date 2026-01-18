# Script de cryptage DPAPI pour les credentials OpenCode
# Chiffre les credentials avec la protection Windows de l'utilisateur courant

param(
    [Parameter(Mandatory=$true)]
    [string]$AnthropicApiKey,

    [Parameter(Mandatory=$true)]
    [string]$AnthropicBaseUrl,

    [Parameter(Mandatory=$true)]
    [string]$TavilyApiKey,

    [Parameter(Mandatory=$false)]
    [string]$OutputPath = "$PSScriptRoot\..\conf_opencode"
)

# Ajouter l'assembly pour la protection des donnees
Add-Type -AssemblyName System.Security

function Protect-String {
    param([string]$PlainText)
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($PlainText)
    $encryptedBytes = [System.Security.Cryptography.ProtectedData]::Protect(
        $bytes,
        $null,
        [System.Security.Cryptography.DataProtectionScope]::CurrentUser
    )
    return [Convert]::ToBase64String($encryptedBytes)
}

try {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  Chiffrement des credentials (DPAPI)" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""

    # Creer le dossier si necessaire
    if (-not (Test-Path $OutputPath)) {
        New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null
    }

    # Chiffrer chaque credential
    $encryptedApiKey = Protect-String -PlainText $AnthropicApiKey
    $encryptedBaseUrl = Protect-String -PlainText $AnthropicBaseUrl
    $encryptedTavily = Protect-String -PlainText $TavilyApiKey

    # Sauvegarder dans un fichier JSON chiffre
    $credentials = @{
        Version = "1.0"
        EncryptedAt = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
        User = $env:USERNAME
        Computer = $env:COMPUTERNAME
        Credentials = @{
            ANTHROPIC_API_KEY = $encryptedApiKey
            ANTHROPIC_BASE_URL = $encryptedBaseUrl
            TAVILY_API_KEY = $encryptedTavily
        }
    }

    $credentialsPath = Join-Path $OutputPath "credentials.encrypted"
    $credentials | ConvertTo-Json -Depth 3 | Set-Content -Path $credentialsPath -Encoding UTF8

    Write-Host "  [OK] Credentials chiffres avec succes" -ForegroundColor Green
    Write-Host "  [OK] Fichier: $credentialsPath" -ForegroundColor Green
    Write-Host ""
    Write-Host "  NOTE: Ces credentials ne peuvent etre dechiffres que" -ForegroundColor Yellow
    Write-Host "        par l'utilisateur '$env:USERNAME' sur cette machine." -ForegroundColor Yellow
    Write-Host ""

    # Supprimer le .env en clair s'il existe
    $envPath = Join-Path $OutputPath ".env"
    if (Test-Path $envPath) {
        Remove-Item $envPath -Force
        Write-Host "  [OK] Fichier .env en clair supprime" -ForegroundColor Green
    }

    exit 0
}
catch {
    Write-Host "  [ERREUR] $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
