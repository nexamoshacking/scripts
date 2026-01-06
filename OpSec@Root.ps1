param (
    [string]$TargetPath,
    [string]$OutputFile = "scan_results.txt",
    [int]$Threads = 6
)

# =========================
# AUTO HELP (no params)
# =========================
if (-not $TargetPath) {
    Write-Host ""
    Write-Host "OPSEC DATA SCANNER (ds.ps1)" -ForegroundColor Cyan
    Write-Host "----------------------------------------"
    Write-Host "Purpose:"
    Write-Host "  Scan directories for sensitive data leaks (OPSEC hygiene)"
    Write-Host ""
    Write-Host "Usage:"
    Write-Host "  .\ds.ps1 -TargetPath <path> [options]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -TargetPath <path>   Directory to scan"
    Write-Host "  -OutputFile <file>   Output file (default: scan_results.txt)"
    Write-Host "  -Threads <n>         Number of threads (default: 6)"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\ds.ps1 -TargetPath C:\Users"
    Write-Host "  .\ds.ps1 -TargetPath C:\ -Threads 12"
    Write-Host ""
    return
}

# =========================
# Regex patterns
# =========================
$Patterns = @{
    Phone_BR   = '(?<!\d)(?:\+55)?(?:[1-9][0-9])9\d{8}(?!\d)'
    CPF        = '(?<!\d)\d{3}\.\d{3}\.\d{3}-\d{2}(?!\d)'
    Email      = '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    IP_Address = '(?<!\d)(?:\d{1,3}\.){3}\d{1,3}(?!\d)'
}

$AllowedExt = ".txt", ".log", ".xml", ".json", ".csv", ".html", ".ini"

# =========================
# Thread-safe storage
# =========================
$Results = @{}
foreach ($Key in $Patterns.Keys) {
    $Results[$Key] = [System.Collections.Concurrent.ConcurrentDictionary[string,bool]]::new()
}

# Progress tracker (REAL thread-safe)
$ProgressTracker = [System.Collections.Concurrent.ConcurrentDictionary[int,bool]]::new()

Write-Host "[*] OPSEC Scan Started" -ForegroundColor Yellow
Write-Host "[*] Target: $TargetPath" -ForegroundColor Yellow

# =========================
# Collect files
# =========================
$Files = Get-ChildItem -Path $TargetPath -Recurse -File -ErrorAction SilentlyContinue |
         Where-Object { $AllowedExt -contains $_.Extension.ToLower() }

$TotalFiles = $Files.Count

Write-Host "[*] Files to scan: $TotalFiles"
Write-Host "----------------------------------------"

# =========================
# Runspace pool
# =========================
$Pool = [runspacefactory]::CreateRunspacePool(1, $Threads)
$Pool.Open()

$Jobs = @()
$Index = 0

foreach ($File in $Files) {

    $FileIndex = $Index
    $Index++

    $PS = [powershell]::Create()
    $PS.RunspacePool = $Pool

    [void]$PS.AddScript({
        param ($File, $Patterns, $Results, $ProgressTracker, $FileIndex)

        try {
            $Lines = [System.IO.File]::ReadLines($File.FullName)
        } catch {
            $ProgressTracker.TryAdd($FileIndex, $true) | Out-Null
            return
        }

        foreach ($Line in $Lines) {
            foreach ($Type in $Patterns.Keys) {
                foreach ($Match in [regex]::Matches($Line, $Patterns[$Type])) {

                    $Value = $Match.Value.Trim()

                    if ($Type -eq "Phone_BR") {
                        $Normalized = $Value -replace '\D',''
                        if ($Normalized.Length -ne 11) { continue }
                    }

                    $Results[$Type].TryAdd($Value, $true) | Out-Null
                }
            }
        }

        $ProgressTracker.TryAdd($FileIndex, $true) | Out-Null

    }).AddArgument($File).AddArgument($Patterns).AddArgument($Results).AddArgument($ProgressTracker).AddArgument($FileIndex)

    $Jobs += [PSCustomObject]@{
        Pipe   = $PS
        Handle = $PS.BeginInvoke()
    }
}

# =========================
# Progress monitor
# =========================
while ($ProgressTracker.Count -lt $TotalFiles) {

    $Done = $ProgressTracker.Count
    $Percent = [math]::Round(($Done / $TotalFiles) * 100, 2)

    Write-Progress `
        -Activity "OPSEC Scan in progress" `
        -Status "$Done / $TotalFiles files scanned" `
        -PercentComplete $Percent

    Start-Sleep -Milliseconds 300
}

Write-Progress -Activity "OPSEC Scan in progress" -Completed

# =========================
# Wait jobs
# =========================
foreach ($Job in $Jobs) {
    $Job.Pipe.EndInvoke($Job.Handle)
    $Job.Pipe.Dispose()
}

$Pool.Close()
$Pool.Dispose()

# =========================
# Output
# =========================
"==== OPSEC DATA SCAN RESULTS ====" | Out-File $OutputFile -Encoding UTF8

foreach ($Type in $Results.Keys) {
    "`n[$Type]" | Out-File $OutputFile -Append -Encoding UTF8
    foreach ($Value in $Results[$Type].Keys) {
        $Value | Out-File $OutputFile -Append -Encoding UTF8
    }
}

Write-Host "----------------------------------------"
Write-Host "[OK] Scan finished" -ForegroundColor Cyan
Write-Host "[OK] Results saved to $OutputFile" -ForegroundColor Cyan
