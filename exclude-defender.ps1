# Script pour exclure les dossiers de Windows Defender
# A executer en tant qu'Administrateur

$installPath = "C:\Program Files\AuxPetitsOignons"
$dataPath = "C:\AuxPetitsOignons"
$opencodePath = "$env:USERPROFILE\.opencode"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Exclusion Windows Defender" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

try {
    # Exclure les dossiers
    Add-MpPreference -ExclusionPath $installPath, $dataPath, $opencodePath
    Write-Host "  [OK] Dossier exclu: $installPath" -ForegroundColor Green
    Write-Host "  [OK] Dossier exclu: $dataPath" -ForegroundColor Green
    Write-Host "  [OK] Dossier exclu: $opencodePath" -ForegroundColor Green

    # Exclure les processus Docker
    try {
        Add-MpPreference -ExclusionProcess 'docker.exe', 'dockerd.exe', 'com.docker.backend.exe'
        Write-Host "  [OK] Processus Docker exclus" -ForegroundColor Green
    } catch {
        Write-Host "  [INFO] Processus Docker deja exclus ou non trouves" -ForegroundColor Yellow
    }

    Write-Host ""
    Write-Host "  Vous pouvez maintenant compiler et lancer l'installeur." -ForegroundColor Yellow
} catch {
    Write-Host "  [ERREUR] Lancez ce script en tant qu'Administrateur !" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Clic droit sur PowerShell > Executer en tant qu'administrateur" -ForegroundColor Yellow
}

Write-Host ""
pause
