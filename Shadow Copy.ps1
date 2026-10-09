# ============================================
# WIN-007 - Shadow Copy Discovery
# Author: Nexamos
# Purpose: Long Life for NXMS
# ============================================

# Forçar encoding do console
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}

# Output setup
$OutputDir = "C:\atc-output\discovery"
if (-not (Test-Path $OutputDir)) { 
    New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null 
}

$RunID = (Get-Date).ToString("yyyyMMdd-HHmmss")
$OutputFile = Join-Path $OutputDir ("WIN-007_ShadowCopyRecon_{0}.txt" -f $RunID)

# Obter hostname local
$computerName = $env:COMPUTERNAME

# Header
$outputLines = @()
$outputLines += "WIN-007 - Shadow Copy Discovery (VSS Reconnaissance)"
$outputLines += "RunID: $RunID"
$outputLines += "Host: $computerName"
$outputLines += "User: $(whoami)"
$outputLines += "Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
$outputLines += ("=" * 80)
$outputLines += ""

# Verificar privilégios administrativos
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
$outputLines += "Executando como Administrador: $(if ($isAdmin) { 'SIM' } else { 'NÃO (algumas informações podem estar limitadas)' })"
$outputLines += ""

$outputLines += "ENUMERANDO SHADOW COPIES NO HOST: $computerName"
$outputLines += ("=" * 80)
$outputLines += ""

# Coletar Shadow Copies via WMI
try {
    $shadowCopies = Get-WmiObject -Class Win32_ShadowCopy -ComputerName $computerName -ErrorAction Stop
    
    if ($shadowCopies) {
        $shadowCount = @($shadowCopies).Count
        $outputLines += "Total de Shadow Copies encontradas: $shadowCount"
        $outputLines += ""
        
        foreach ($shadow in $shadowCopies) {
            $outputLines += "--- Shadow Copy ---"
            $outputLines += "ID: $($shadow.ID)"
            $outputLines += "DeviceObject: $($shadow.DeviceObject)"
            $outputLines += "VolumeName: $($shadow.VolumeName)"
            $outputLines += "InstallDate: $($shadow.InstallDate)"
            $outputLines += "OriginatingMachine: $($shadow.OriginatingMachine)"
            
            # Calcular idade da shadow copy
            if ($shadow.InstallDate) {
                try {
                    $installDate = [System.Management.ManagementDateTimeConverter]::ToDateTime($shadow.InstallDate)
                    $age = (Get-Date) - $installDate
                    $outputLines += "Idade: $($age.Days) dias, $($age.Hours) horas"
                } catch {
                    $outputLines += "Idade: (não disponível)"
                }
            }
            
            $outputLines += ""
        }
        
        # Resumo por volume
        $outputLines += ("=" * 80)
        $outputLines += "RESUMO POR VOLUME"
        $outputLines += ("=" * 80)
        $volumeGroups = $shadowCopies | Group-Object -Property VolumeName
        foreach ($group in $volumeGroups) {
            $outputLines += "Volume: $($group.Name) - Shadow Copies: $($group.Count)"
        }
        $outputLines += ""
        
    } else {
        $outputLines += "NENHUMA SHADOW COPY ENCONTRADA"
        $outputLines += ""
        $outputLines += "ALERTA: Sistema não possui Shadow Copies ativas."
        $outputLines += "        Sem backups VSS disponíveis para recuperação."
        $outputLines += ""
    }
    
} catch {
    $outputLines += "ERRO ao enumerar Shadow Copies via WMI"
    $outputLines += "Erro: $($_.Exception.Message)"
    $outputLines += ""
    
    # Tentar método alternativo com vssadmin
    $outputLines += "Tentando método alternativo (vssadmin)..."
    $outputLines += ""
    
    try {
        $vssOutput = vssadmin list shadows 2>&1
        if ($LASTEXITCODE -eq 0) {
            $outputLines += "Saída do vssadmin list shadows:"
            $outputLines += ("-" * 40)
            foreach ($line in $vssOutput) {

Papis Nexamos, [22/10/2025 10:42]
$outputLines += $line
            }
            $outputLines += ("-" * 40)
        } else {
            $outputLines += "vssadmin também falhou (código: $LASTEXITCODE)"
        }
    } catch {
        $outputLines += "Erro ao executar vssadmin: $($_.Exception.Message)"
    }
    $outputLines += ""
}

# Verificar serviço VSS
$outputLines += ("=" * 80)
$outputLines += "STATUS DO SERVIÇO VSS"
$outputLines += ("=" * 80)

try {
    $vssService = Get-Service -Name VSS -ErrorAction Stop
    $outputLines += "Nome: $($vssService.Name)"
    $outputLines += "DisplayName: $($vssService.DisplayName)"
    $outputLines += "Status: $($vssService.Status)"
    $outputLines += "StartType: $($vssService.StartType)"
} catch {
    $outputLines += "Erro ao obter status do serviço VSS: $($_.Exception.Message)"
}

$outputLines += ""
$outputLines += ("=" * 80)
$outputLines += "RECONHECIMENTO CONCLUÍDO"
$outputLines += ("=" * 80)
$outputLines += ""
$outputLines += "NOTA: Este script apenas enumera Shadow Copies (audit-only)."
$outputLines += "      Comportamento típico de ransomware para reconhecimento."
$outputLines += "      Nenhuma modificação foi realizada no sistema."

# Salvar com BOM UTF-8 para compatibilidade com Windows PowerShell
try {
    $text = $outputLines -join "`r`n"
    $utf8 = [System.Text.Encoding]::UTF8
    $bom = $utf8.GetPreamble()
    $bytes = $utf8.GetBytes($text)
    $outBytes = New-Object byte[] ($bom.Length + $bytes.Length)
    [System.Array]::Copy($bom, 0, $outBytes, 0, $bom.Length)
    [System.Array]::Copy($bytes, 0, $outBytes, $bom.Length, $bytes.Length)
    [System.IO.File]::WriteAllBytes($OutputFile, $outBytes)
    
    Write-Output ""
    Write-Output "Shadow Copy Discovery concluído!"
    Write-Output "Arquivo: $OutputFile"
    Write-Output "Host: $computerName"
} catch {
    Write-Output "Erro ao salvar arquivo: $($_.Exception.Message)"
}