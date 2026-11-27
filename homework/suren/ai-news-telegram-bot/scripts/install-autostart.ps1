<#
Start the interactive digest bot automatically when you log in to Windows: no console window,
restarted if it crashes, logs in bot.log in the project folder.

    .\scripts\install-autostart.ps1              # install and start now
    .\scripts\install-autostart.ps1 -Uninstall   # stop and remove

The bot only answers while this PC is on and you are logged in.
#>
param([switch]$Uninstall)
$ErrorActionPreference = "Stop"

$TaskName = "AI News Telegram Bot"
$Root = Split-Path -Parent $PSScriptRoot
$User = "$env:USERDOMAIN\$env:USERNAME"

if ($Uninstall) {
    try { Stop-ScheduledTask -TaskName $TaskName -ErrorAction Stop } catch {}
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Host "Removed scheduled task '$TaskName'."
    return
}

$Pythonw = Join-Path $Root ".venv\Scripts\pythonw.exe"
if (-not (Test-Path $Pythonw)) { throw "Missing $Pythonw. Create the virtual environment first (README: Local setup)." }
if (-not (Test-Path (Join-Path $Root ".env"))) { throw "Missing .env with TELEGRAM_BOT_TOKEN (README: Store the token locally)." }

$action = New-ScheduledTaskAction -Execute $Pythonw -Argument "-m bot --log-file bot.log" -WorkingDirectory $Root
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $User
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable `
    -ExecutionTimeLimit ([TimeSpan]::Zero) -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1) `
    -MultipleInstances IgnoreNew
$principal = New-ScheduledTaskPrincipal -UserId $User -LogonType Interactive -RunLevel Limited

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings `
    -Principal $principal -Description "Telegram bot: sends the AI news digest when a user presses the button." -Force | Out-Null
Start-ScheduledTask -TaskName $TaskName
Write-Host "Installed and started '$TaskName'. Logs: $(Join-Path $Root 'bot.log')"
