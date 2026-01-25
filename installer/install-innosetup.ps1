# Script pour installer Inno Setup automatiquement

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Installation Inno Setup 6" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier si Inno Setup est déjà installé
$innoPath = "C:\Program Files (x86)\Inno Setup 6\iscc.exe"

if (Test-Path $innoPath) {
    Write-Host "Inno Setup 6 est deja installe !" -ForegroundColor Green
    Write-Host "Emplacement: $innoPath" -ForegroundColor Green
    Write-Host ""
    Write-Host "Pour compiler l'installeur, lancez:" -ForegroundColor Cyan
    Write-Host "  .\compile.bat" -ForegroundColor White
    Write-Host ""
    exit 0
}

Write-Host "Inno Setup n'est pas installe." -ForegroundColor Yellow
Write-Host ""

$answer = Read-Host "Voulez-vous le telecharger et l'installer maintenant ? (O/N)"

if ($answer -ne "O" -and $answer -ne "o") {
    Write-Host ""
    Write-Host "Installation annulee." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Pour installer manuellement:" -ForegroundColor Cyan
    Write-Host "  1. Visitez: https://jrsoftware.org/isdl.php" -ForegroundColor White
    Write-Host "  2. Telechargez Inno Setup 6.3.3 ou superieur" -ForegroundColor White
    Write-Host "  3. Installez avec les options par defaut" -ForegroundColor White
    Write-Host "  4. Relancez ce script" -ForegroundColor White
    Write-Host ""
    exit 0
}

Write-Host ""
Write-Host "Telechargement d'Inno Setup 6..." -ForegroundColor Yellow

# URL de téléchargement Inno Setup 6.3.3
$innoSetupUrl = "https://jrsoftware.org/download.php/is.exe"
$installerPath = "$env:TEMP\innosetup-install.exe"

try {
    # Télécharger
    Write-Host "URL: $innoSetupUrl" -ForegroundColor Gray
    Invoke-WebRequest -Uri $innoSetupUrl -OutFile $installerPath -UseBasicParsing

    Write-Host "Telechargement termine." -ForegroundColor Green
    Write-Host ""
    Write-Host "Lancement de l'installation..." -ForegroundColor Yellow
    Write-Host "Suivez les instructions a l'ecran." -ForegroundColor Yellow
    Write-Host ""

    # Lancer l'installeur
    Start-Process -FilePath $installerPath -Wait

    Write-Host ""
    Write-Host "Verification de l'installation..." -ForegroundColor Yellow

    if (Test-Path $innoPath) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "  Installation reussie !" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Inno Setup 6 est maintenant installe." -ForegroundColor Green
        Write-Host ""
        Write-Host "Pour compiler l'installeur, lancez:" -ForegroundColor Cyan
        Write-Host "  .\compile.bat" -ForegroundColor White
        Write-Host ""
    } else {
        Write-Host ""
        Write-Host "Inno Setup ne semble pas avoir ete installe." -ForegroundColor Red
        Write-Host "Verifiez que l'installation s'est bien deroulee." -ForegroundColor Yellow
        Write-Host ""
    }

    # Nettoyer
    Remove-Item $installerPath -ErrorAction SilentlyContinue

} catch {
    Write-Host ""
    Write-Host "Erreur lors du telechargement:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Write-Host "Telechargez manuellement depuis:" -ForegroundColor Yellow
    Write-Host "https://jrsoftware.org/isdl.php" -ForegroundColor White
    Write-Host ""
    exit 1
}
