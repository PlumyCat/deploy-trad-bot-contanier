@echo off
echo(
echo ========================================
echo   Preparation de l'installation
echo ========================================
echo(
echo Ce script doit etre lance en Administrateur
echo pour autoriser l'installeur a s'executer
echo(
pause

:: Detecter le dossier OneDrive Be-Cloud
set "ONEDRIVE_BECLOUD=%USERPROFILE%\OneDrive - Be-Cloud"

if not exist "%ONEDRIVE_BECLOUD%" (
    echo(
    echo Dossier OneDrive Be-Cloud non trouve
    echo Chemin attendu: %ONEDRIVE_BECLOUD%
    echo(
    pause
    exit /b 1
)

echo(
echo Ajout des exclusions Windows Defender..
echo(

powershell -ExecutionPolicy Bypass -Command "Add-MpPreference -ExclusionPath '%ONEDRIVE_BECLOUD%\Aux_Petits_Oignons', 'C:\Program Files\AuxPetitsOignons', 'C:\Program Files (x86)\AuxPetitsOignons', '%LOCALAPPDATA%\Programs\AuxPetitsOignons', '%USERPROFILE%\AuxPetitsOignons', '%USERPROFILE%\AppData\AuxPetitsOignons', '%USERPROFILE%\.opencode'; Add-MpPreference -ExclusionProcess 'docker.exe', 'dockerd.exe', 'com.docker.backend.exe'"

if errorlevel 1 (
    echo(
    echo [ERREUR] Lancez ce script en tant qu'Administrateur !
    echo(
    echo Clic droit ^> Executer en tant qu'administrateur
    echo(
) else (
    echo(
    echo [OK] Exclusions ajoutees avec succes !
    echo(
    echo Vous pouvez maintenant lancer AuxPetitsOignons_Setup.exe
    echo(
)

pause
