@echo off
echo.
echo ========================================
echo   Invalid Distribution Cleanup
echo ========================================
echo.
echo This will clean up temporary folders that cause pip warnings.
echo Python must be CLOSED for this to work.
echo.
pause
echo.
powershell -ExecutionPolicy Bypass -File "%~dp0cleanup_invalid_distributions.ps1"
