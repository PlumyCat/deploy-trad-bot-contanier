@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   Preparation de l'installation
echo ========================================
echo.
echo Ce script doit etre lance en Administrateur
echo pour autoriser l'installeur a s'executer.
echo.
pause

:: Detecter le dossier OneDrive Be-Cloud
set "ONEDRIVE_BECLOUD=%USERPROFILE%\OneDrive - Be-Cloud"

if not exist "%ONEDRIVE_BECLOUD%" (
    echo.
    echo Dossier OneDrive Be-Cloud non trouve.
    echo Chemin attendu: %ONEDRIVE_BECLOUD%
    echo.
    pause
    exit /b 1
)

echo.
echo Ajout des exclusions Windows Defender...
echo.

powershell -ExecutionPolicy Bypass -Command ^
    "Add-MpPreference -AttackSurfaceReductionOnlyExclusions '%ONEDRIVE_BECLOUD%\Aux_Petits_Oignons'; ^
     Add-MpPreference -ExclusionPath '%ONEDRIVE_BECLOUD%\Aux_Petits_Oignons'"

if errorlevel 1 (
    echo.
    echo [ERREUR] Lancez ce script en tant qu'Administrateur !
    echo.
    echo Clic droit ^> Executer en tant qu'administrateur
    echo.
) else (
    echo.
    echo [OK] Exclusions ajoutees avec succes !
    echo.
    echo Vous pouvez maintenant lancer AuxPetitsOignons_Setup.exe
    echo.
)

pause
