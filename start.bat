@echo off
echo(
echo ========================================
echo   Aux Petits Oignons
echo ========================================
echo(

set "SCRIPT_DIR=%~dp0"
set "CONFIG_FILE=%SCRIPT_DIR%conf_opencode\.env"
set "ENCRYPTED_FILE=%SCRIPT_DIR%conf_opencode\credentials.encrypted"
set "DATA_DIR=%USERPROFILE%\AuxPetitsOignons"
set "REPO_CONFIG=%SCRIPT_DIR%repo-config.txt"

:: ========================================
:: Creation des dossiers de donnees
:: ========================================
if not exist "%DATA_DIR%" (
    echo Creation du dossier de donnees..
    mkdir "%DATA_DIR%"
)
if not exist "%DATA_DIR%\clients" mkdir "%DATA_DIR%\clients"
if not exist "%DATA_DIR%\Solution" mkdir "%DATA_DIR%\Solution"

:: ========================================
:: Gestion des credentials (chiffres ou non)
:: ========================================

:: Verifier si on a des credentials chiffres
if exist "%ENCRYPTED_FILE%" (
    echo Dechiffrement des credentials..
    powershell.exe -ExecutionPolicy Bypass -File "%SCRIPT_DIR%scripts\decrypt-credentials.ps1" ^
        -CredentialsPath "%ENCRYPTED_FILE%" ^
        -OutputPath "%CONFIG_FILE%" >nul 2>&1

    if errorlevel 2 (
        echo(
        echo ========================================
        echo   ERREUR: Credentials invalides
        echo ========================================
        echo(
        echo Les credentials ont ete chiffres par un autre utilisateur
        echo Veuillez reconfigurer avec: configure.bat
        echo(
        pause
        exit /b 1
    )
    if errorlevel 1 (
        echo(
        echo Erreur lors du dechiffrement. Lancement de la configuration..
        echo(
        call "%SCRIPT_DIR%configure.bat"
    ) else (
        echo Credentials dechiffres avec succes
    )
) else if not exist "%CONFIG_FILE%" (
    :: Pas de fichier chiffre ni de .env, lancer la configuration
    echo Configuration non trouvee. Lancement de la configuration..
    echo(
    call "%SCRIPT_DIR%configure.bat"

    :: Re-verifier apres configuration
    if exist "%ENCRYPTED_FILE%" (
        echo Dechiffrement des credentials..
        powershell.exe -ExecutionPolicy Bypass -File "%SCRIPT_DIR%scripts\decrypt-credentials.ps1" ^
            -CredentialsPath "%ENCRYPTED_FILE%" ^
            -OutputPath "%CONFIG_FILE%" >nul 2>&1
    )
)

:: Verifier qu'on a bien un fichier de config maintenant
if not exist "%CONFIG_FILE%" (
    echo(
    echo Erreur: Configuration requise pour continuer
    pause
    exit /b 1
)

:: ========================================
:: Verification Docker
:: ========================================
docker info >nul 2>&1
if errorlevel 1 (
    echo(
    echo ========================================
    echo   ERREUR: Docker n'est pas demarre !
    echo ========================================
    echo(
    echo Veuillez demarrer Docker Desktop puis relancer ce script
    echo(
    goto :cleanup
)

echo(
echo Demarrage du container..
echo(

:: Arreter et supprimer le container existant s'il existe
docker stop trad-bot-opencode >nul 2>&1
docker rm trad-bot-opencode >nul 2>&1

:: Demarrer le container (avec --force-recreate pour garantir l'execution de l'entrypoint)
echo Attente que le container soit pret (health check)..
docker-compose up -d --force-recreate --wait
if errorlevel 1 (
    echo(
    echo ========================================
    echo   ERREUR: Echec du demarrage Docker
    echo ========================================
    echo(
    echo Verifiez les logs ci-dessus pour plus de details
    echo(
    goto :cleanup
)

:: Supprimer le fichier .env en clair immediatement apres le demarrage
if exist "%ENCRYPTED_FILE%" (
    if exist "%CONFIG_FILE%" (
        del "%CONFIG_FILE%" >nul 2>&1
    )
)

echo(
echo Ouverture de la documentation..
start http://localhost:5545/procedure

echo(
echo ========================================
echo   Container pret !
echo ========================================
echo(
echo   Commandes disponibles :
echo(
echo     opencode      - Nouvelle conversation
echo     opencode -c   - REPRENDRE la conversation precedente
echo(
echo   Si la conversation a ete coupee, utilisez: opencode -c
echo(
echo ========================================
echo(
docker exec -it trad-bot-opencode bash

:: ========================================
:: Nettoyage a la sortie
:: ========================================
:cleanup
echo(
echo ========================================
echo   Session terminee
echo ========================================
echo(

:: Arreter le container
echo Arret du container..
docker-compose down >nul 2>&1

:: Supprimer le fichier .env en clair si on a un fichier chiffre
if exist "%ENCRYPTED_FILE%" (
    if exist "%CONFIG_FILE%" (
        echo Nettoyage des credentials temporaires..
        del "%CONFIG_FILE%" >nul 2>&1
    )
)

echo   Pour reprendre plus tard : relancez start.bat
echo   puis tapez: opencode -c
echo(
pause
