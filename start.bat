@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   🧅 Aux Petits Oignons
echo ========================================
echo.

set "CONFIG_FILE=%~dp0conf_opencode\.env"

:: Vérifier si la configuration existe
if not exist "%CONFIG_FILE%" (
    echo Configuration non trouvee. Lancement de la configuration...
    echo.
    call "%~dp0configure.bat"
)

:: Vérifier que le fichier a bien été créé
if not exist "%CONFIG_FILE%" (
    echo.
    echo Erreur: Configuration requise pour continuer.
    pause
    exit /b 1
)

:: Vérifier que Docker est démarré
docker info >nul 2>&1
if errorlevel 1 (
    echo.
    echo ========================================
    echo   ERREUR: Docker n'est pas demarre !
    echo ========================================
    echo.
    echo Veuillez demarrer Docker Desktop puis relancer ce script.
    echo.
    pause
    exit /b 1
)

:: ========================================
:: Connexion Azure (sur Windows = navigateur)
:: ========================================
echo.
echo Verification de la connexion Azure...
az account show >nul 2>&1
if errorlevel 1 (
    echo.
    echo ========================================
    echo   Connexion Azure requise
    echo ========================================
    echo.
    set /p TENANT_ID="Entrez le Tenant ID du client (ou Entree pour passer): "
    if defined TENANT_ID (
        echo.
        echo Connexion au tenant %TENANT_ID%...
        az login --tenant %TENANT_ID%
    ) else (
        echo.
        echo Connexion Azure standard...
        az login
    )
    if errorlevel 1 (
        echo.
        echo Erreur de connexion Azure.
        pause
        exit /b 1
    )
    echo.
    echo Connexion Azure reussie !
) else (
    echo Deja connecte a Azure.
    az account show --query "{Compte:user.name, Tenant:tenantId}" -o table
    echo.
    set /p CHANGE_TENANT="Changer de tenant ? (O/N): "
    if /i "%CHANGE_TENANT%"=="O" (
        set /p TENANT_ID="Entrez le nouveau Tenant ID: "
        az logout
        az login --tenant %TENANT_ID%
    )
)

echo Demarrage du container...
echo.

:: Arrêter et supprimer le container existant s'il existe
docker stop trad-bot-opencode >nul 2>&1
docker rm trad-bot-opencode >nul 2>&1

:: Démarrer le container
docker-compose up -d
if errorlevel 1 (
    echo.
    echo ========================================
    echo   ERREUR: Echec du demarrage Docker
    echo ========================================
    echo.
    echo Verifiez les logs ci-dessus pour plus de details.
    echo.
    pause
    exit /b 1
)

echo.
echo Ouverture de la documentation...
start http://localhost:5545/procedure

echo.
echo Connexion au container...
echo.
echo Pour lancer OpenCode, tapez: opencode
echo.
docker exec -it trad-bot-opencode bash

:: Si on arrive ici après exit du container, on pause pour voir les messages
echo.
echo Session terminee.
pause
