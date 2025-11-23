# Allow Zeyta AI Server through Windows Firewall
# Run this script as Administrator if other devices can't connect

Write-Host "🔥 Configuring Windows Firewall for Zeyta AI Server..." -ForegroundColor Cyan
Write-Host ""

# Get Python executable path
$pythonPath = (Get-Command python).Source

# Create firewall rule for Python
Write-Host "Creating firewall rule for Python..." -ForegroundColor Yellow
try {
    New-NetFirewallRule `
        -DisplayName "Zeyta AI - Python Server" `
        -Direction Inbound `
        -Program $pythonPath `
        -Action Allow `
        -Profile Private,Public `
        -ErrorAction Stop
    Write-Host "✅ Python firewall rule created successfully!" -ForegroundColor Green
} catch {
    if ($_.Exception.Message -like "*already exists*") {
        Write-Host "ℹ️  Python firewall rule already exists" -ForegroundColor Yellow
    } else {
        Write-Host "❌ Failed to create Python rule: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Create firewall rule for port 5000
Write-Host "`nCreating firewall rule for port 5000..." -ForegroundColor Yellow
try {
    New-NetFirewallRule `
        -DisplayName "Zeyta AI - Port 5000" `
        -Direction Inbound `
        -Protocol TCP `
        -LocalPort 5000 `
        -Action Allow `
        -Profile Private,Public `
        -ErrorAction Stop
    Write-Host "✅ Port 5000 firewall rule created successfully!" -ForegroundColor Green
} catch {
    if ($_.Exception.Message -like "*already exists*") {
        Write-Host "ℹ️  Port 5000 firewall rule already exists" -ForegroundColor Yellow
    } else {
        Write-Host "❌ Failed to create port rule: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`n✅ Firewall configuration complete!" -ForegroundColor Green
Write-Host "🌐 Your server should now be accessible from other devices on the network" -ForegroundColor Cyan
Write-Host "📱 Access from: https://10.0.0.66:5000" -ForegroundColor Cyan
Write-Host "⚠️  Note: You will see a certificate warning. Click 'Advanced' -> 'Proceed' to continue." -ForegroundColor Yellow
Write-Host ""
