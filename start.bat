@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   Aux Petits Oignons
echo ========================================
echo.

set "SCRIPT_DIR=%~dp0"
set "CONFIG_FILE=%SCRIPT_DIR%conf_opencode\.env"
set "ENCRYPTED_FILE=%SCRIPT_DIR%conf_opencode\credentials.encrypted"
set "DATA_DIR=C:\AuxPetitsOignons"
set "SRC_DIR=%DATA_DIR%\src"
set "REPO_CONFIG=%SCRIPT_DIR%repo-config.txt"

:: ========================================
:: Lecture de la config du repo
:: ========================================
set "REPO_URL=https://github.com/PlumyCat/trad-bot-src.git"
set "REPO_BRANCH=main"

if exist "%REPO_CONFIG%" (
    for /f "tokens=1,* delims==" %%a in ('findstr /v "^#" "%REPO_CONFIG%"') do (
        if "%%a"=="REPO_URL" set "REPO_URL=%%b"
        if "%%a"=="REPO_BRANCH" set "REPO_BRANCH=%%b"
    )
)

:: ========================================
:: Mise a jour du code source depuis GitHub
:: ========================================
echo Verification du code source...

:: Verifier si Git est installe
git --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ========================================
    echo   ATTENTION: Git n'est pas installe
    echo ========================================
    echo.
    echo Pour les mises a jour automatiques, installez Git:
    echo https://git-scm.com/download/win
    echo.
    if not exist "%SRC_DIR%" (
        echo Le dossier src/ n'existe pas et ne peut pas etre telecharge.
        echo.
        pause
        exit /b 1
    )
    echo Utilisation du code existant...
    goto :skip_git
)

:: Creer le dossier de donnees si necessaire
if not exist "%DATA_DIR%" (
    echo Creation du dossier de donnees...
    mkdir "%DATA_DIR%"
    mkdir "%DATA_DIR%\clients"
    mkdir "%DATA_DIR%\Solution"
)

:: Clone ou mise a jour du repo
if not exist "%SRC_DIR%\.git" (
    echo.
    echo Telechargement du code source...
    echo Repository: %REPO_URL%
    echo.

    :: Supprimer le dossier src s'il existe mais n'est pas un repo git
    if exist "%SRC_DIR%" (
        rmdir /s /q "%SRC_DIR%"
    )

    git clone --branch %REPO_BRANCH% --single-branch "%REPO_URL%" "%SRC_DIR%"
    if errorlevel 1 (
        echo.
        echo ERREUR: Impossible de cloner le repository.
        echo Verifiez votre connexion internet.
        echo.
        pause
        exit /b 1
    )
    echo.
    echo Code source telecharge avec succes !
) else (
    echo Mise a jour du code source...
    pushd "%SRC_DIR%"
    git fetch origin %REPO_BRANCH% >nul 2>&1

    :: Verifier s'il y a des mises a jour
    for /f %%i in ('git rev-parse HEAD') do set "LOCAL_HASH=%%i"
    for /f %%i in ('git rev-parse origin/%REPO_BRANCH%') do set "REMOTE_HASH=%%i"

    if not "%LOCAL_HASH%"=="%REMOTE_HASH%" (
        echo Nouvelle version disponible, mise a jour...
        git pull origin %REPO_BRANCH%
        if errorlevel 1 (
            echo.
            echo ATTENTION: Mise a jour echouee, utilisation de la version locale.
            echo.
        ) else (
            echo Mise a jour terminee !
        )
    ) else (
        echo Code source deja a jour.
    )
    popd
)

:skip_git

:: ========================================
:: Gestion des credentials (chiffres ou non)
:: ========================================

:: Verifier si on a des credentials chiffres
if exist "%ENCRYPTED_FILE%" (
    echo Dechiffrement des credentials...
    powershell.exe -ExecutionPolicy Bypass -File "%SCRIPT_DIR%scripts\decrypt-credentials.ps1" ^
        -CredentialsPath "%ENCRYPTED_FILE%" ^
        -OutputPath "%CONFIG_FILE%" >nul 2>&1

    if errorlevel 2 (
        echo.
        echo ========================================
        echo   ERREUR: Credentials invalides
        echo ========================================
        echo.
        echo Les credentials ont ete chiffres par un autre utilisateur.
        echo Veuillez reconfigurer avec: configure.bat
        echo.
        pause
        exit /b 1
    )
    if errorlevel 1 (
        echo.
        echo Erreur lors du dechiffrement. Lancement de la configuration...
        echo.
        call "%SCRIPT_DIR%configure.bat"
    ) else (
        echo Credentials dechiffres avec succes.
    )
) else if not exist "%CONFIG_FILE%" (
    :: Pas de fichier chiffre ni de .env, lancer la configuration
    echo Configuration non trouvee. Lancement de la configuration...
    echo.
    call "%SCRIPT_DIR%configure.bat"

    :: Re-verifier apres configuration
    if exist "%ENCRYPTED_FILE%" (
        echo Dechiffrement des credentials...
        powershell.exe -ExecutionPolicy Bypass -File "%SCRIPT_DIR%scripts\decrypt-credentials.ps1" ^
            -CredentialsPath "%ENCRYPTED_FILE%" ^
            -OutputPath "%CONFIG_FILE%" >nul 2>&1
    )
)

:: Verifier qu'on a bien un fichier de config maintenant
if not exist "%CONFIG_FILE%" (
    echo.
    echo Erreur: Configuration requise pour continuer.
    pause
    exit /b 1
)

:: ========================================
:: Verification Docker
:: ========================================
docker info >nul 2>&1
if errorlevel 1 (
    echo.
    echo ========================================
    echo   ERREUR: Docker n'est pas demarre !
    echo ========================================
    echo.
    echo Veuillez demarrer Docker Desktop puis relancer ce script.
    echo.
    goto :cleanup
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
        goto :cleanup
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

:: Arreter et supprimer le container existant s'il existe
docker stop trad-bot-opencode >nul 2>&1
docker rm trad-bot-opencode >nul 2>&1

:: Demarrer le container
docker-compose up -d
if errorlevel 1 (
    echo.
    echo ========================================
    echo   ERREUR: Echec du demarrage Docker
    echo ========================================
    echo.
    echo Verifiez les logs ci-dessus pour plus de details.
    echo.
    goto :cleanup
)

echo.
echo Ouverture de la documentation...
start http://localhost:5545/procedure

echo.
echo ========================================
echo   Container pret !
echo ========================================
echo.
echo   Commandes disponibles :
echo.
echo     opencode      - Nouvelle conversation
echo     opencode -c   - REPRENDRE la conversation precedente
echo.
echo   Si la conversation a ete coupee, utilisez: opencode -c
echo.
echo ========================================
echo.
docker exec -it trad-bot-opencode bash

:: ========================================
:: Nettoyage a la sortie
:: ========================================
:cleanup
echo.
echo ========================================
echo   Session terminee
echo ========================================
echo.

:: Supprimer le fichier .env en clair si on a un fichier chiffre
if exist "%ENCRYPTED_FILE%" (
    if exist "%CONFIG_FILE%" (
        echo Nettoyage des credentials temporaires...
        del "%CONFIG_FILE%" >nul 2>&1
    )
)

echo   Pour reprendre plus tard : relancez start.bat
echo   puis tapez: opencode -c
echo.
pause
