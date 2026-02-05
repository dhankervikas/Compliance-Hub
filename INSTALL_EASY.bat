@echo off
REM ====================================================================
REM AssuRisk Complete Auto-Installer - Windows Launcher
REM ====================================================================
REM Just double-click this file and enter your API key when prompted!
REM ====================================================================

echo.
echo ========================================
echo   AssuRisk Complete Auto-Installer
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed!
    echo.
    echo Please install Python from: https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo [OK] Python found
echo.

REM Get API key from user
echo Please enter your Gemini API key.
echo Get one at: https://ai.google.dev/gemini-api/docs/api-key
echo.
set /p GEMINI_KEY="Enter API key: "

if "%GEMINI_KEY%"=="" (
    echo.
    echo ERROR: No API key entered!
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Starting Installation...
echo   This will take 5-7 minutes
echo ========================================
echo.

REM Run the complete installer
python complete_installer.py --api-key %GEMINI_KEY%

if errorlevel 1 (
    echo.
    echo ========================================
    echo   Installation Failed
    echo ========================================
    echo.
    echo Please check the error messages above.
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo Next step: Generate your first policies
echo.
echo Run: cd Backend
echo Then: python generate_policies.py
echo.
pause
