# Variables
$APIKey = "KEY" #JC Api Key used to authenticate to pwsh
$AutomationPath = "C:\Scripts\" # Absolute path to the automation
$CSVOutput = "$AutomationPath\Audit\JumpCloud_InactiveDevices.csv" # Path to store CSV reports locally
$LogFolderPath = "$AutomationPath\Audit\Logs" # Log Folder absolute path
$LogFileName = "Audit-$(Get-Date -Format 'yyyyMMdd').txt" # Log filename
$LogFilePath = Join-Path -Path $LogFolderPath -ChildPath $LogFileName #Log file path using the absolute log  path
$PythonPath = "python.exe" # the symlink does not always work for python, so i found out that giving the path to python solves this issue
$HiBobFetcher = "$AutomationPath\Audit\HiBobFetcher.py" # HiBobFetcher path
$GoogleSheetsUploader = "$AutomationPath\Audit\GoogleSheetsUploader.py" #GoogleSheetsUploader path
$GoogleSheetID = "SHEET_ID"  #  Google Sheet ID for storing the report
$GoogleSheetTabName = "JumpCloud Report $(Get-Date -Format 'yyyyMMddHHmm')" # Generates a new teb with current date
$GoogleIgnoreTabName = "Ignore List"
$IgnoreListPath = "$AutomationPath\Audit\IgnoreList.json"
$GoogleScriptPath = "$AutomationPath\Audit\GoogleSheetsIgnoreFetcher.py"
$SlackWebhookURL = "webhook_url"  # Slack WebHook URL
$SlackChannel = "#channel_name"  # Channel name where to post the message
$SlackUserTags = "<@user_id>"  # User ID who to mention in channel

# Ensure log directory exists
if (!(Test-Path $LogFolderPath)) {
    New-Item -ItemType Directory -Path $LogFolderPath -Force | Out-Null
}
# Connect to JC
Connect-JCOnline -JumpCloudAPIKey $APIKey -Force

$SlackStartMessage = @{
    text = ":rocket: *JumpCloud Device Audit* has started running in Jenkins!"
    channel = $SlackChannel
}
Invoke-RestMethod -Uri $SlackWebhookURL -Method Post -Body ($SlackStartMessage | ConvertTo-Json -Depth 3) -ContentType "application/json"

Start-Process -FilePath $PythonPath -ArgumentList "$GoogleScriptPath $GoogleSheetID $GoogleIgnoreTabName" -NoNewWindow -Wait

# Read Ignore List
$IgnoreList = @()
if (Test-Path $IgnoreListPath) {
    $IgnoreList = Get-Content -Path $IgnoreListPath | ConvertFrom-Json | Select-Object -ExpandProperty DeviceName
}

# Query all devices from JC
$Devices = Get-JCSystem
$DeviceReport = @()

foreach ($Device in $Devices) {
    $DeviceName = if ($Device.hostname) { $Device.hostname } else { $Device.displayName }
    $Architecture = if ($Device.os) { $Device.os } else { "Unknown" }

    if ($IgnoreList -contains $DeviceName) {
        continue
    }

    if ([string]::IsNullOrEmpty($Device.lastContact)) {
        continue
    }

    try {
        $LastContact = [DateTime]::Parse($Device.lastContact)
    } catch {
        continue
    }

    $ThresholdDate = (Get-Date).AddDays(-16)
    if ($LastContact -gt $ThresholdDate) {
        continue
    }

    $DaysOffline = ((Get-Date) - $LastContact).Days

    $BoundUsers = Get-JCSystemUser -SystemID $Device.id
    $UserEmails = @()
    $UserStatuses = @()
    $UserIDs = @()

    if ($BoundUsers.Count -eq 0) {
        $UserEmails = "None"
        $UserStatuses = "None"
        $UserIDs = "None"
    } else {
        foreach ($BoundUser in $BoundUsers) {
            if (-not [string]::IsNullOrEmpty($BoundUser.Username)) {
                $UserDetails = Get-JCUser -Username $BoundUser.Username
                $UserEmails += $UserDetails.email
                $UserStatuses += if ($UserDetails.suspended) { "Suspended" } else { "Active" }
                $UserIDs += $UserDetails.id
            }
        }
    }

    $UserEmailsString = $UserEmails -join "`r`n"
    $UserStatusesString = $UserStatuses -join "`r`n"
    $UserIDsString = $UserIDs -join "`r`n"

    $DeviceReport += [PSCustomObject]@{
        "DeviceName"       = $DeviceName
        "DeviceID"         = $Device.id
        "Architecture"     = $Architecture
        "LastContact"      = $LastContact
        "Days Offline"     = $DaysOffline
        "BoundUserEmails"  = $UserEmailsString
        "UserID"           = $UserIDsString
        "BoundUserStatuses" = $UserStatusesString
    }
}

# Write to python
$DeviceReportJson = $DeviceReport | ConvertTo-Json -Depth 3
$DeviceReportJson | Out-File -FilePath "$AutomationPath\Audit\JumpCloudData.json" -Encoding UTF8

# Run HiBob API Fetcher
Start-Process -FilePath $PythonPath -ArgumentList "$HiBobFetcher $GoogleSheetID" -NoNewWindow -Wait

# Run Google Sheets Uploader
Start-Process -FilePath $PythonPath -ArgumentList "$GoogleSheetsUploader $GoogleSheetID `"$GoogleSheetTabName`"" -NoNewWindow -Wait

# Slack Notification
$GoogleSheetURL = "https://docs.google.com/spreadsheets/d/$GoogleSheetID"
$SlackFinalMessage = @{
    text = ":white_check_mark: *JumpCloud Device Audit* completed! Report added to Google Sheets: <$GoogleSheetURL> $SlackUserTags"
    channel = $SlackChannel
}
Invoke-RestMethod -Uri $SlackWebhookURL -Method Post -Body ($SlackFinalMessage | ConvertTo-Json -Depth 3) -ContentType "application/json"

Write-Host "JumpCloud audit completed successfully."
