# PowerShell script to clean up invalid distribution folders
# Run this script when Python is NOT running

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Invalid Distribution Cleanup Tool" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$sitePackages = "C:\Users\Rayan\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\site-packages"

Write-Host "Checking for invalid distributions in:" -ForegroundColor Yellow
Write-Host "  $sitePackages`n" -ForegroundColor Gray

# Find all folders starting with ~
$invalidDirs = Get-ChildItem -Path $sitePackages -Directory -Filter "~*" -ErrorAction SilentlyContinue

if ($invalidDirs.Count -eq 0) {
    Write-Host "✓ No invalid distributions found!" -ForegroundColor Green
    Write-Host "`nPress any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 0
}

Write-Host "Found $($invalidDirs.Count) invalid distribution folders:" -ForegroundColor Yellow
foreach ($dir in $invalidDirs) {
    Write-Host "  - $($dir.Name)" -ForegroundColor Gray
}

Write-Host "`nAttempting to remove..." -ForegroundColor Yellow

# Check if any Python processes are running
$pythonProcesses = Get-Process python* -ErrorAction SilentlyContinue
if ($pythonProcesses) {
    Write-Host "`n⚠️  WARNING: Python is currently running!" -ForegroundColor Red
    Write-Host "  Please close all Python processes first:" -ForegroundColor Yellow
    foreach ($proc in $pythonProcesses) {
        Write-Host "    - $($proc.Name) (PID: $($proc.Id))" -ForegroundColor Gray
    }
    Write-Host "`nWould you like to kill these processes? (Y/N): " -ForegroundColor Yellow -NoNewline
    $response = Read-Host
    
    if ($response -eq 'Y' -or $response -eq 'y') {
        foreach ($proc in $pythonProcesses) {
            try {
                Stop-Process -Id $proc.Id -Force
                Write-Host "  ✓ Killed $($proc.Name) (PID: $($proc.Id))" -ForegroundColor Green
            }
            catch {
                Write-Host "  ✗ Failed to kill $($proc.Name): $_" -ForegroundColor Red
            }
        }
        Start-Sleep -Seconds 2
    }
    else {
        Write-Host "`nPlease close Python processes manually and run this script again." -ForegroundColor Yellow
        Write-Host "`nPress any key to exit..."
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        exit 1
    }
}

# Try to remove each invalid directory
$successCount = 0
$failCount = 0

foreach ($dir in $invalidDirs) {
    try {
        Remove-Item -Path $dir.FullName -Recurse -Force -ErrorAction Stop
        Write-Host "  ✓ Removed: $($dir.Name)" -ForegroundColor Green
        $successCount++
    }
    catch {
        Write-Host "  ✗ Failed: $($dir.Name) - $($_.Exception.Message)" -ForegroundColor Red
        $failCount++
    }
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Cleanup Results:" -ForegroundColor Cyan
Write-Host "  Successfully removed: $successCount" -ForegroundColor Green
Write-Host "  Failed to remove: $failCount" -ForegroundColor $(if ($failCount -gt 0) { "Red" } else { "Green" })
Write-Host "========================================`n" -ForegroundColor Cyan

if ($failCount -gt 0) {
    Write-Host "⚠️  Some files could not be removed because they are locked." -ForegroundColor Yellow
    Write-Host "   This is normal and they will be cleaned up automatically." -ForegroundColor Yellow
    Write-Host "   You can safely ignore the warnings in pip output.`n" -ForegroundColor Yellow
}
else {
    Write-Host "✅ All invalid distributions cleaned successfully!`n" -ForegroundColor Green
}

Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
