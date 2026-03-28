@echo off
setlocal enabledelayedexpansion

echo ============================================
echo   InvoiceScrapper -- Windows Build
echo ============================================
echo.

echo [1/3] Installing / upgrading PyInstaller...
pip install pyinstaller --upgrade --quiet
if !ERRORLEVEL! NEQ 0 (
    echo ERROR: pip install failed. Is Python in your PATH?
    pause & exit /b 1
)

echo [2/3] Installing project dependencies...
pip install requests pandas openpyxl PyQt6 --quiet

echo [3/3] Building InvoiceScrapper.exe ...
pyinstaller invoice.spec --clean --noconfirm

echo.
if !ERRORLEVEL! == 0 (
    echo ============================================
    echo   Build successful!
    echo   Output: dist\InvoiceScrapper.exe
    echo ============================================
) else (
    echo ============================================
    echo   Build FAILED -- check output above
    echo ============================================
)

endlocal
pause
