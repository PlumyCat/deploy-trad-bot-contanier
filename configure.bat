@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   Aux Petits Oignons - Configuration
echo ========================================
echo.

set "SCRIPT_DIR=%~dp0"
set "ENCRYPTED_FILE=%SCRIPT_DIR%conf_opencode\credentials.encrypted"

if exist "%ENCRYPTED_FILE%" (
    echo Configuration existante detectee (chiffree).
    echo.
    set /p OVERWRITE="Voulez-vous la modifier ? (O/N) : "
    if /i "%OVERWRITE%"=="N" (
        echo Configuration conservee.
        goto :end
    )
    if /i "%OVERWRITE%"=="NON" (
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
echo Configuration Tavily (MCP Search)
echo ----------------------------------
echo.
echo Cle API disponible sur https://tavily.com
echo.

set /p TAVILY_KEY="TAVILY_API_KEY : "

echo.
echo Chiffrement des credentials...
echo.

:: Appeler le script PowerShell de chiffrement
powershell.exe -ExecutionPolicy Bypass -File "%SCRIPT_DIR%scripts\encrypt-credentials.ps1" ^
    -AnthropicApiKey "%API_KEY%" ^
    -AnthropicBaseUrl "%BASE_URL%" ^
    -TavilyApiKey "%TAVILY_KEY%" ^
    -OutputPath "%SCRIPT_DIR%conf_opencode"

if errorlevel 1 (
    echo.
    echo ========================================
    echo   ERREUR lors du chiffrement
    echo ========================================
    echo.
    echo Tentative de sauvegarde en mode compatible...
    echo.

    :: Fallback: sauvegarder en clair si le chiffrement echoue
    (
        echo ANTHROPIC_API_KEY=%API_KEY%
        echo ANTHROPIC_BASE_URL=%BASE_URL%
        echo TAVILY_API_KEY=%TAVILY_KEY%
    ) > "%SCRIPT_DIR%conf_opencode\.env"

    echo Configuration sauvegardee en mode non-chiffre.
    echo Pour plus de securite, relancez configure.bat.
) else (
    echo.
    echo ========================================
    echo   Configuration chiffree avec succes
    echo ========================================
    echo.
    echo Vos credentials sont proteges par DPAPI Windows.
    echo Ils ne peuvent etre utilises que par votre compte utilisateur.
)

:end
echo.
pause
