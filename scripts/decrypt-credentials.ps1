# Script de decryptage DPAPI pour les credentials OpenCode
# Dechiffre les credentials et cree un fichier .env temporaire

param(
    [Parameter(Mandatory=$false)]
    [string]$CredentialsPath = "$PSScriptRoot\..\conf_opencode\credentials.encrypted",

    [Parameter(Mandatory=$false)]
    [string]$OutputPath = "$PSScriptRoot\..\conf_opencode\.env"
)

# Ajouter l'assembly pour la protection des donnees
Add-Type -AssemblyName System.Security

function Unprotect-String {
    param([string]$EncryptedBase64)
    $encryptedBytes = [Convert]::FromBase64String($EncryptedBase64)
    $decryptedBytes = [System.Security.Cryptography.ProtectedData]::Unprotect(
        $encryptedBytes,
        $null,
        [System.Security.Cryptography.DataProtectionScope]::CurrentUser
    )
    return [System.Text.Encoding]::UTF8.GetString($decryptedBytes)
}

try {
    if (-not (Test-Path $CredentialsPath)) {
        Write-Host "Fichier de credentials chiffres non trouve." -ForegroundColor Yellow
        exit 1
    }

    # Charger le fichier JSON chiffre
    $credentials = Get-Content -Path $CredentialsPath -Raw | ConvertFrom-Json

    # Dechiffrer chaque credential
    $apiKey = Unprotect-String -EncryptedBase64 $credentials.Credentials.ANTHROPIC_API_KEY
    $baseUrl = Unprotect-String -EncryptedBase64 $credentials.Credentials.ANTHROPIC_BASE_URL
    $tavilyKey = Unprotect-String -EncryptedBase64 $credentials.Credentials.TAVILY_API_KEY

    # Creer le fichier .env
    $envContent = @"
# Fichier genere automatiquement - NE PAS MODIFIER
# Les vraies credentials sont stockees de facon chiffree
ANTHROPIC_API_KEY=$apiKey
ANTHROPIC_BASE_URL=$baseUrl
TAVILY_API_KEY=$tavilyKey
"@

    Set-Content -Path $OutputPath -Value $envContent -Encoding UTF8

    # Retourner le chemin pour le script appelant
    Write-Output $OutputPath
    exit 0
}
catch [System.Security.Cryptography.CryptographicException] {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "  ERREUR: Impossible de dechiffrer" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Les credentials ont ete chiffres par un autre" -ForegroundColor Yellow
    Write-Host "  utilisateur ou sur une autre machine." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  Veuillez reconfigurer avec: configure.bat" -ForegroundColor Yellow
    Write-Host ""
    exit 2
}
catch {
    Write-Host "  [ERREUR] $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
