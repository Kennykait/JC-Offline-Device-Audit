$ThresholdDate = (Get-Date).AddDays(-16)
$CurrentDate = Get-Date
$DeviceReport = @()

$IgnoreList = @()
if (Test-Path $IgnoreListPath) {
    $IgnoreList = Get-Content -Path $IgnoreListPath | ConvertFrom-Json | Select-Object -ExpandProperty DeviceName
    Write-Log "Loaded ignore list with $($IgnoreList.Count) entries."
}

$Devices = Get-JCSystem

foreach ($Device in $Devices) {
    $DeviceName = if ($Device.hostname) { $Device.hostname } else { $Device.displayName }
    if ($IgnoreList -contains $DeviceName) {
        Write-Log "Skipping $DeviceName (ignored)"
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

    if ($LastContact -gt $ThresholdDate) {
        continue
    }

    $DaysOffline = ($CurrentDate - $LastContact).Days
    $Architecture = if ($Device.os) { $Device.os } else { "Unknown" }

    $BoundUsers = Get-JCSystemUser -SystemID $Device.id
    $UserEmails = @()
    $UserStatuses = @()
    $UserIDs = @()

    foreach ($BoundUser in $BoundUsers) {
        if (-not [string]::IsNullOrEmpty($BoundUser.Username)) {
            $UserDetails = Get-JCUser -Username $BoundUser.Username
            $UserEmails += $UserDetails.email
            $UserStatuses += (if ($UserDetails.suspended) { "Suspended" } else { "Active" })
            $UserIDs += $UserDetails.id
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
        "User Emails"      = $UserEmailsString
        "UserID"           = $UserIDsString
        "Account Status"   = $UserStatusesString
    }

    Write-Log "Processed $DeviceName ($DaysOffline days offline)"
}

# Write audit data to JSON
$DeviceReport | ConvertTo-Json -Depth 4 | Out-File -FilePath $JumpCloudJson -Encoding UTF8
Write-Log "Audit data written to $JumpCloudJson"
