# Script pour exclure ce dossier de Windows Defender
# A executer en tant qu'Administrateur

$currentPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$installPath = "C:\Program Files\AuxPetitsOignons"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Exclusion Windows Defender" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

try {
    Add-MpPreference -ExclusionPath $currentPath, $installPath
    Write-Host "  [OK] Dossier exclu: $currentPath" -ForegroundColor Green
    Write-Host "  [OK] Dossier exclu: $installPath" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Vous pouvez maintenant compiler et lancer l'installeur." -ForegroundColor Yellow
} catch {
    Write-Host "  [ERREUR] Lancez ce script en tant qu'Administrateur !" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Clic droit sur PowerShell > Executer en tant qu'administrateur" -ForegroundColor Yellow
}

Write-Host ""
pause
