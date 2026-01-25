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

:: ========================================
:: Verification image Docker
:: ========================================
docker images auxpetitsoignons-trad-bot:latest | findstr "auxpetitsoignons-trad-bot" >nul 2>&1
if errorlevel 1 (
    echo(
    echo ========================================
    echo   Premier lancement - Build de l'image
    echo ========================================
    echo(
    echo L'image Docker va etre creee (environ 2-3 minutes)
    echo Puis installation OpenCode au demarrage (environ 6 minutes)
    echo(
    echo Veuillez patienter...
    echo(

    cd "%SCRIPT_DIR%"

    REM Activer BuildKit
    set DOCKER_BUILDKIT=1
    set COMPOSE_DOCKER_CLI_BUILD=1

    echo Build de l'image Docker...
    docker build -t auxpetitsoignons-trad-bot:latest . 2>&1

    if errorlevel 1 (
        echo(
        echo ========================================
        echo   ERREUR lors du build
        echo ========================================
        echo(
        echo Verifiez que Docker Desktop est bien demarre
        echo et que vous avez une connexion Internet
        echo(
        goto :cleanup
    )

    echo(
    echo ========================================
    echo   Build termine avec succes
    echo ========================================
    echo(
)

echo(
echo Demarrage du container..
echo(

:: Verifier si le container existe deja
docker ps -a --filter "name=trad-bot-opencode" --format "{{.Names}}" | findstr "trad-bot-opencode" >nul 2>&1
if errorlevel 1 (
    :: Container n'existe pas, le creer
    echo Creation du container...
    docker-compose up -d
    if errorlevel 1 (
        echo(
        echo ========================================
        echo   ERREUR: Echec de la creation
        echo ========================================
        echo(
        goto :cleanup
    )
) else (
    :: Container existe, le demarrer
    echo Demarrage du container existant...
    docker start trad-bot-opencode >nul 2>&1
    if errorlevel 1 (
        echo(
        echo Container corrompu, recreation...
        docker rm trad-bot-opencode >nul 2>&1
        docker-compose up -d
        if errorlevel 1 (
            echo(
            echo ========================================
            echo   ERREUR: Echec du demarrage
            echo ========================================
            echo(
            goto :cleanup
        )
    )
)

echo(
echo Attente du demarrage du container...
timeout /t 5 /nobreak >nul

:: Verifier si c'est le premier demarrage (installation Bun)
docker exec trad-bot-opencode test -f /opt/aux-petits-oignons/.build_done >nul 2>&1
if errorlevel 1 (
    echo(
    echo ========================================
    echo   PREMIER DEMARRAGE DETECTE
    echo ========================================
    echo(
    echo Installation OpenCode en cours (environ 6 minutes)
    echo Vous pouvez suivre la progression dans une autre fenetre avec:
    echo   docker logs -f trad-bot-opencode
    echo(
    echo Attente de la fin de l'installation...

    :wait_build
    timeout /t 10 /nobreak >nul
    docker exec trad-bot-opencode test -f /opt/aux-petits-oignons/.build_done >nul 2>&1
    if errorlevel 1 goto :wait_build

    echo(
    echo ========================================
    echo   Installation terminee
    echo ========================================
    echo(
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

echo Ouverture d'OpenCode dans une nouvelle fenetre..
start cmd /k "%~dp0launch-opencode.bat"

echo(
echo ========================================
echo   Container pret !
echo ========================================
echo(
echo   Une fenetre OpenCode s'est ouverte automatiquement
echo   Le navigateur affiche la documentation Power Platform
echo(
echo   Dans la fenetre OpenCode :
echo     - Tapez vos questions ou demandes
echo     - Pour reprendre : fermez et relancez start.bat
echo       puis tapez: opencode -c
echo(
echo   Pour arreter le container :
echo     - Fermez cette fenetre OU tapez Ctrl+C
echo(
echo ========================================
echo(
echo Fenetre de controle (ne pas fermer pendant utilisation)
echo Appuyez sur Ctrl+C pour arreter le container
echo(
pause >nul

:: ========================================
:: Nettoyage a la sortie
:: ========================================
:cleanup
echo(
echo ========================================
echo   Session terminee
echo ========================================
echo(

:: Arreter le container (sans le supprimer)
echo Arret du container..
docker stop trad-bot-opencode >nul 2>&1

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
