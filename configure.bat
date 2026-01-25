@echo off
echo(
echo ========================================
echo   Aux Petits Oignons - Configuration
echo ========================================
echo(

set "SCRIPT_DIR=%~dp0"
set "CONFIG_FILE=%SCRIPT_DIR%conf_opencode\.env"
set "ENCRYPTED_FILE=%SCRIPT_DIR%conf_opencode\credentials.encrypted"

if exist "%ENCRYPTED_FILE%" (
    echo Configuration existante (chiffree)
    echo(
    set /p OVERWRITE="Voulez-vous la modifier (O/N) : "
    if /i "%OVERWRITE%"=="N" (
        echo Configuration conservee
        goto :end
    )
    if /i "%OVERWRITE%"=="NON" (
        echo Configuration conservee
        goto :end
    )
)

echo(
echo Configuration Azure AI Foundry
echo -----------------------------------------
echo(
echo Ces informations sont disponibles dans Azure AI Foundry
echo(

set /p AZURE_AI_FOUNDRY_ENDPOINT="AZURE_AI_FOUNDRY_ENDPOINT : "
set /p AZURE_API_KEY="AZURE_API_KEY : "

echo(
echo Configuration Azure OpenAI
echo -----------------------------------------
echo(
echo Ces informations sont disponibles dans Azure OpenAI Studio
echo(

set /p AZURE_OPENAI_ENDPOINT="AZURE_OPENAI_ENDPOINT : "
set /p AZURE_OPENAI_API_KEY="AZURE_OPENAI_API_KEY : "

echo(
echo Configuration Tavily (MCP Search - Optionnel)
echo ----------------------------------
echo(
echo Cle API disponible sur https://tavily.com
echo Laissez vide si vous ne voulez pas activer la recherche web
echo(

set /p TAVILY_KEY="TAVILY_API_KEY (optionnel) : "

if "%TAVILY_KEY%"=="" (
    set TAVILY_KEY=tvly-your_tavily_key_here
)

echo(
echo Sauvegarde de la configuration...
echo(

(
    echo # Configuration Azure AI Foundry pour Aux petits Oignons
    echo.
    echo.
    echo # ============================================================================
    echo # Endpoint 2 : Model-Router (Azure AI Foundry^)
    echo # ============================================================================
    echo AZURE_AI_FOUNDRY_ENDPOINT=%AZURE_AI_FOUNDRY_ENDPOINT%
    echo AZURE_API_KEY=%AZURE_API_KEY%
    echo.
    echo.
    echo # ============================================================================
    echo # Endpoint 3 : GPT-4.1 Mini + GPT-5 Mini (Azure OpenAI^)
    echo # Les 2 modeles OpenAI partagent le meme endpoint
    echo # ============================================================================
    echo AZURE_OPENAI_ENDPOINT=%AZURE_OPENAI_ENDPOINT%
    echo AZURE_OPENAI_API_KEY=%AZURE_OPENAI_API_KEY%
    echo.
    echo.
    echo # ============================================================================
    echo # Configuration Tavily (MCP Search^)
    echo # ============================================================================
    echo TAVILY_API_KEY=%TAVILY_KEY%
) > "%CONFIG_FILE%"

echo(
echo ========================================
echo   Configuration sauvegardee
echo ========================================
echo(
echo Le fichier .env est pret dans conf_opencode\
echo(

:end
echo(
pause
