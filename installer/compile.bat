@echo off
chcp 65001 > nul
echo.
echo ========================================
echo   Compilation Installeur .exe
echo   Aux petits oignons v1.3
echo ========================================
echo.

REM Chercher Inno Setup dans les emplacements standards
set ISCC_PATH=

if exist "C:\Program Files (x86)\Inno Setup 6\iscc.exe" (
    set ISCC_PATH=C:\Program Files ^(x86^)\Inno Setup 6\iscc.exe
)

if exist "C:\Program Files (x86)\Inno Setup 5\iscc.exe" (
    set ISCC_PATH=C:\Program Files ^(x86^)\Inno Setup 5\iscc.exe
)

if exist "C:\Program Files\Inno Setup 6\iscc.exe" (
    set ISCC_PATH=C:\Program Files\Inno Setup 6\iscc.exe
)

if "%ISCC_PATH%"=="" (
    echo.
    echo [ERREUR] Inno Setup n'est pas installe
    echo.
    echo Telechargez et installez Inno Setup depuis:
    echo https://jrsoftware.org/isdl.php
    echo.
    echo Version recommandee: Inno Setup 6.3.3 ou superieure
    echo.
    pause
    exit /b 1
)

echo Compilateur Inno Setup trouve:
echo %ISCC_PATH%
echo.
echo Compilation en cours...
echo.

REM Compiler le setup
"%ISCC_PATH%" setup.iss

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   COMPILATION REUSSIE !
    echo ========================================
    echo.
    echo Installeur cree:
    echo output\AuxPetitsOignons_Setup.exe
    echo.

    REM Afficher la taille du fichier
    for %%F in (output\AuxPetitsOignons_Setup.exe) do (
        set size=%%~zF
        set /a size_mb=!size! / 1048576
        echo Taille: !size_mb! MB
    )

    echo.
    echo Vous pouvez maintenant distribuer cet installeur.
    echo.
) else (
    echo.
    echo [ERREUR] La compilation a echoue
    echo.
    echo Verifiez les erreurs ci-dessus.
    echo.
)

pause
