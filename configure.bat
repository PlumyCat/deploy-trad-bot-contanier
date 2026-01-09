@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   🧅 Aux Petits Oignons - Configuration
echo ========================================
echo.

set "CONFIG_FILE=%~dp0conf_opencode\.env"

if exist "%CONFIG_FILE%" (
    echo Configuration existante detectee.
    echo.
    set /p OVERWRITE="Voulez-vous la modifier ? (O/N) : "
    if /i not "%OVERWRITE%"=="O" (
        echo Configuration conservee.
        goto :end
    )
)

echo.
echo Configuration d'OpenCode (Azure Foundry)
echo -----------------------------------------
echo.
echo Ces informations sont disponibles dans Azure AI Foundry.
echo.

set /p API_KEY="ANTHROPIC_API_KEY : "
set /p BASE_URL="ANTHROPIC_BASE_URL : "

echo.
echo Enregistrement de la configuration...

(
echo ANTHROPIC_API_KEY=%API_KEY%
echo ANTHROPIC_BASE_URL=%BASE_URL%
) > "%CONFIG_FILE%"

echo.
echo ✓ Configuration enregistree dans conf_opencode\.env
echo.

:end
pause
