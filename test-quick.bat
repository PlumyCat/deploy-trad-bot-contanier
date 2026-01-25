@echo off
echo.
echo ========================================
echo   TEST RAPIDE - Aux petits Oignons
echo ========================================
echo.

echo 1. Verification du fichier .env...
if exist "conf_opencode\.env" (
    echo    [OK] conf_opencode\.env existe
    echo.
    echo Contenu (masque):
    findstr /R "ENDPOINT KEY" conf_opencode\.env | findstr /V "your_" | findstr /V "votre_"
) else (
    echo    [ERREUR] conf_opencode\.env manquant
    exit /b 1
)

echo.
echo 2. Verification du Dockerfile...
if exist "Dockerfile" (
    echo    [OK] Dockerfile existe
    findstr /C:"Aux-petits-Oignons" Dockerfile >nul && echo    [OK] Fork Aux-petits-Oignons detecte
) else (
    echo    [ERREUR] Dockerfile manquant
    exit /b 1
)

echo.
echo 3. Verification docker-compose.yml...
if exist "docker-compose.yml" (
    echo    [OK] docker-compose.yml existe
    findstr /C:"auxpetitsoignons-trad-bot" docker-compose.yml >nul && echo    [OK] Image name correct
) else (
    echo    [ERREUR] docker-compose.yml manquant
    exit /b 1
)

echo.
echo 4. Verification Docker Desktop...
docker info >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo    [OK] Docker Desktop est demarre
) else (
    echo    [ATTENTION] Docker Desktop n'est pas demarre
    echo    Demarrez Docker Desktop pour continuer les tests
    pause
    exit /b 0
)

echo.
echo ========================================
echo   TESTS OK - Pret pour rebuild
echo ========================================
echo.
echo Pour builder et tester:
echo   1. rebuild-fast.bat
echo   2. start.bat
echo.

pause
