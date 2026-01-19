@echo off
REM ============================================
REM Rebuild Docker Image
REM ============================================
REM Force une reconstruction complete de l'image
REM Docker pour corriger les problemes de build
REM ============================================

echo.
echo ========================================
echo   REBUILD COMPLET DE L'IMAGE DOCKER
echo ========================================
echo.

echo Arret du container...
docker-compose down 2>nul

echo Suppression de l'image existante...
docker rmi auxpetitsoignons-trad-bot 2>nul
docker rmi deploy-trad-bot-contanier-trad-bot 2>nul

echo.
echo Reconstruction de l'image (OPTIMISEE)...
echo Debut: %TIME%
echo.
docker-compose build --no-cache

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Fin: %TIME%
    echo.
    echo ========================================
    echo   IMAGE RECONSTRUITE AVEC SUCCES
    echo ========================================
    echo.
    echo Taille de l'image:
    docker images deploy-trad-bot-contanier-trad-bot-opencode
    echo.
    echo Pour demarrer le container :
    echo   start.bat
    echo.
) else (
    echo.
    echo ========================================
    echo   ERREUR: Echec du rebuild
    echo ========================================
    echo.
)

pause
