@echo off
echo Test du menu
set /p CHOICE="Tapez 4 : "
echo Vous avez tape: [%CHOICE%]
echo.

if "%CHOICE%"=="1" (
    echo Option 1
    goto :end
) else if "%CHOICE%"=="2" (
    echo Option 2
    goto :end
) else if "%CHOICE%"=="3" (
    echo Option 3
    goto :end
) else if "%CHOICE%"=="4" (
    echo Option 4 - CORRECT!
    goto :end
) else (
    echo Choix invalide
)

:end
pause
