@echo off
REM ============================================
REM Rebuild ULTRA-RAPIDE avec BuildKit
REM ============================================
echo.
echo ========================================
echo   REBUILD ULTRA-RAPIDE (BuildKit)
echo ========================================
echo.

REM Activer BuildKit
set DOCKER_BUILDKIT=1
set COMPOSE_DOCKER_CLI_BUILD=1

echo Arret du container...
docker-compose down 2>nul

echo Suppression de l'image existante...
docker rmi deploy-trad-bot-contanier-trad-bot-opencode 2>nul

echo.
echo Choisissez la version :
echo.
echo   1. BuildKit + Cache Mounts        [9-10 min] (STABLE)
echo   2. Binaire func direct            [7-8 min]  (EXPERIMENTAL)
echo   3. Image Microsoft avec func      [6-7 min]  (EXPERIMENTAL)
echo   4. Fork Aux-petits-Oignons        [12-15 min] (CUSTOM) *** NOUVEAU ***
echo   5. Build standard                 [15 min]
echo.
set /p CHOICE="Votre choix (1/2/3/4/5) : "

if "%CHOICE%"=="1" (
    echo.
    echo ========================================
    echo   Option 1: BuildKit Cache Mounts
    echo ========================================
    echo.
    echo Build avec Dockerfile.optimized...
    echo Debut: %TIME%
    echo.

    docker build -f Dockerfile.optimized -t deploy-trad-bot-contanier-trad-bot-opencode:latest .

    REM Verifier si l'image existe (plus fiable que ERRORLEVEL avec BuildKit)
    docker images -q deploy-trad-bot-contanier-trad-bot-opencode:latest > nul 2>&1

    if %ERRORLEVEL% EQU 0 (
        echo.
        echo Fin: %TIME%
        echo.
        echo ========================================
        echo   BUILD REUSSI
        echo ========================================
        echo.
        docker images deploy-trad-bot-contanier-trad-bot-opencode
        echo.
        echo Pour demarrer: start.bat
        echo.
    ) else (
        echo.
        echo ERREUR lors du build
        echo.
    )
    goto :end
) else if "%CHOICE%"=="2" (
    echo.
    echo ========================================
    echo   Option 2: Version ULTRA-RAPIDE
    echo ========================================
    echo.
    echo Build avec Dockerfile.ultra-fast...
    echo Debut: %TIME%
    echo.

    docker build -f Dockerfile.ultra-fast -t deploy-trad-bot-contanier-trad-bot-opencode:latest .

    REM Verifier si l'image existe
    docker images -q deploy-trad-bot-contanier-trad-bot-opencode:latest > nul 2>&1

    if %ERRORLEVEL% EQU 0 (
        echo.
        echo Fin: %TIME%
        echo.
        echo ========================================
        echo   BUILD REUSSI
        echo ========================================
        echo.
        docker images deploy-trad-bot-contanier-trad-bot-opencode
        echo.
        echo Pour demarrer: start.bat
        echo.
    ) else (
        echo.
        echo ERREUR lors du build
        echo.
    )
    goto :end
) else if "%CHOICE%"=="3" (
    echo.
    echo ========================================
    echo   Option 3: Image Microsoft MCR
    echo ========================================
    echo.
    echo ATTENTION: Cette option est experimentale (Alpine Linux)
    echo.
    echo Build avec Dockerfile.from-mcr...
    echo Debut: %TIME%
    echo.

    docker build -f Dockerfile.from-mcr -t deploy-trad-bot-contanier-trad-bot-opencode:latest .

    REM Verifier si l'image existe
    docker images -q deploy-trad-bot-contanier-trad-bot-opencode:latest > nul 2>&1

    if %ERRORLEVEL% EQU 0 (
        echo.
        echo Fin: %TIME%
        echo.
        echo ========================================
        echo   BUILD REUSSI
        echo ========================================
        echo.
        docker images deploy-trad-bot-contanier-trad-bot-opencode
        echo.
        echo Pour demarrer: start.bat
        echo.
    ) else (
        echo.
        echo ERREUR lors du build
        echo.
    )
    goto :end
) else if "%CHOICE%"=="4" (
    echo.
    echo ========================================
    echo   Option 4: Fork Aux-petits-Oignons
    echo ========================================
    echo.
    echo Version personnalisee avec:
    echo   - 4 modeles Azure pre-configures
    echo   - Welcome page Aux petits Oignons
    echo   - Config entreprise verrouillee
    echo.
    echo Build avec Dockerfile.custom-opencode...
    echo Debut: %TIME%
    echo.

    docker build -f Dockerfile.custom-opencode -t deploy-trad-bot-contanier-trad-bot-opencode:latest .

    REM Verifier si l'image existe
    docker images -q deploy-trad-bot-contanier-trad-bot-opencode:latest > nul 2>&1

    if %ERRORLEVEL% EQU 0 (
        echo.
        echo Fin: %TIME%
        echo.
        echo ========================================
        echo   BUILD REUSSI - FORK CUSTOM
        echo ========================================
        echo.
        docker images deploy-trad-bot-contanier-trad-bot-opencode
        echo.
        echo IMPORTANT: N'oubliez pas de configurer .env avec:
        echo   - ANTHROPIC_BASE_URL
        echo   - ANTHROPIC_API_KEY
        echo   - AZURE_OPENAI_ENDPOINT
        echo   - AZURE_OPENAI_API_KEY
        echo.
        echo Pour demarrer: start.bat
        echo.
    ) else (
        echo.
        echo ERREUR lors du build
        echo.
    )
    goto :end
) else (
    echo.
    echo Build standard...
    echo Debut: %TIME%
    echo.
    docker-compose build --no-cache
    echo.
    echo Fin: %TIME%
    echo.
)

:end
pause
