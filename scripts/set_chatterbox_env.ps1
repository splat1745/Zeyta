# Set CHATTERBOX_PYTHON environment variable persistently for the current user
# This allows tts_test.py to use the isolated chatterbox venv on CUDA

$chatterboxPython = "e:\AI-OFFICIAL\AI-RELEASE\venv_chatterbox\Scripts\python.exe"

Write-Host "Setting CHATTERBOX_PYTHON environment variable to: $chatterboxPython"
[System.Environment]::SetEnvironmentVariable('CHATTERBOX_PYTHON', $chatterboxPython, 'User')

Write-Host ""
Write-Host "Environment variable set successfully!"
Write-Host "Please restart your terminal or VS Code for the change to take effect."
Write-Host ""
Write-Host "To verify, run: `$env:CHATTERBOX_PYTHON"
Write-Host ""
Write-Host "Now tts_test.py will use Chatterbox on CUDA via subprocess when using cinematic mode."
