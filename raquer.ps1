Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# ================= FUNÇÕES =================
function Eh-IP($valor) {
    return $valor -match '^\d{1,3}(\.\d{1,3}){3}$'
}

function Eh-Admin {
    $id = [Security.Principal.WindowsIdentity]::GetCurrent()
    $p  = New-Object Security.Principal.WindowsPrincipal($id)
    return $p.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Garantir-TrustedHost($ip) {
    if (-not (Eh-Admin)) {
        throw "Execute o PowerShell como ADMINISTRADOR."
    }

    $trusted = (Get-Item WSMan:\localhost\Client\TrustedHosts).Value

    if (-not $trusted) {
        Set-Item WSMan:\localhost\Client\TrustedHosts -Value $ip -Force
    }
    elseif ($trusted -notmatch $ip) {
        Set-Item WSMan:\localhost\Client\TrustedHosts -Value "$trusted,$ip" -Force
    }
}

function Atualizar-Processos($destino) {
    $lstProcessos.Items.Clear()

    $processos = Invoke-Command -ComputerName $destino -ScriptBlock {
        Get-Process | Sort-Object Name | Select Name, Id
    }

    foreach ($p in $processos) {
        $lstProcessos.Items.Add("$($p.Name) [$($p.Id)]")
    }
}

# ================= CORES DARK NEON =================
$DarkBg = [System.Drawing.Color]::FromArgb(18,18,18)
$CardBg = [System.Drawing.Color]::FromArgb(28,28,28)
$NeonRed = [System.Drawing.Color]::FromArgb(255,40,40)
$DarkRed = [System.Drawing.Color]::FromArgb(120,0,0)
$TextLight = [System.Drawing.Color]::FromArgb(230,230,230)

# ================= FORM =================
$form = New-Object System.Windows.Forms.Form
$form.Text = "LOKI - HORA DE TRAVESSURAS RS"
$form.Size = New-Object System.Drawing.Size(560,600)
$form.StartPosition = "CenterScreen"
$form.FormBorderStyle = 'FixedDialog'
$form.MaximizeBox = $false
$form.BackColor = $DarkBg

# ================= HEADER =================
$panelHeader = New-Object System.Windows.Forms.Panel
$panelHeader.Size = New-Object System.Drawing.Size(560,70)
$panelHeader.BackColor = [System.Drawing.Color]::FromArgb(10,10,10)
$form.Controls.Add($panelHeader)

$lblTitle = New-Object System.Windows.Forms.Label
$lblTitle.Text = "CONTROLE TUDO QUE QUISER - FDS"
$lblTitle.Font = New-Object System.Drawing.Font("Segoe UI",14,[System.Drawing.FontStyle]::Bold)
$lblTitle.ForeColor = $NeonRed
$lblTitle.AutoSize = $true
$lblTitle.Location = New-Object System.Drawing.Point(20,15)
$panelHeader.Controls.Add($lblTitle)

$lblDev = New-Object System.Windows.Forms.Label
$lblDev.Text = "Criado por Nexamos"
$lblDev.Font = New-Object System.Drawing.Font("Segoe UI",9)
$lblDev.ForeColor = $TextLight
$lblDev.AutoSize = $true
$lblDev.Location = New-Object System.Drawing.Point(22,42)
$panelHeader.Controls.Add($lblDev)

# ================= CARD CONEXÃO =================
$panelConn = New-Object System.Windows.Forms.Panel
$panelConn.Location = New-Object System.Drawing.Point(20,85)
$panelConn.Size = New-Object System.Drawing.Size(510,90)
$panelConn.BackColor = $CardBg
$panelConn.BorderStyle = 'FixedSingle'
$form.Controls.Add($panelConn)

$lblComp = New-Object System.Windows.Forms.Label
$lblComp.Text = "Nome/IP fdp"
$lblComp.ForeColor = $TextLight
$lblComp.Font = New-Object System.Drawing.Font("Segoe UI",9,[System.Drawing.FontStyle]::Bold)
$lblComp.Location = New-Object System.Drawing.Point(15,15)
$panelConn.Controls.Add($lblComp)

$txtComp = New-Object System.Windows.Forms.TextBox
$txtComp.Location = New-Object System.Drawing.Point(18,40)
$txtComp.Size = New-Object System.Drawing.Size(300,25)
$txtComp.BackColor = [System.Drawing.Color]::FromArgb(40,40,40)
$txtComp.ForeColor = $TextLight
$txtComp.BorderStyle = 'FixedSingle'
$panelConn.Controls.Add($txtComp)

$btnConectar = New-Object System.Windows.Forms.Button
$btnConectar.Text = "Conectar"
$btnConectar.Location = New-Object System.Drawing.Point(340,38)
$btnConectar.Size = New-Object System.Drawing.Size(140,30)
$btnConectar.FlatStyle = 'Flat'
$btnConectar.BackColor = $NeonRed
$btnConectar.ForeColor = 'White'
$panelConn.Controls.Add($btnConectar)

# ================= LISTA =================
$lstProcessos = New-Object System.Windows.Forms.ListBox
$lstProcessos.Location = New-Object System.Drawing.Point(20,190)
$lstProcessos.Size = New-Object System.Drawing.Size(510,280)
$lstProcessos.BackColor = [System.Drawing.Color]::FromArgb(25,25,25)
$lstProcessos.ForeColor = $TextLight
$lstProcessos.Font = New-Object System.Drawing.Font("Consolas",9)
$form.Controls.Add($lstProcessos)

# ================= BOTÕES =================
$btnFinalizar = New-Object System.Windows.Forms.Button
$btnFinalizar.Text = "Finalizar Processo"
$btnFinalizar.Location = New-Object System.Drawing.Point(40,500)
$btnFinalizar.Size = New-Object System.Drawing.Size(200,40)
$btnFinalizar.FlatStyle = 'Flat'
$btnFinalizar.BackColor = $DarkRed
$btnFinalizar.ForeColor = 'White'
$form.Controls.Add($btnFinalizar)

$btnAtualizar = New-Object System.Windows.Forms.Button
$btnAtualizar.Text = "Atualizar Lista"
$btnAtualizar.Location = New-Object System.Drawing.Point(300,500)
$btnAtualizar.Size = New-Object System.Drawing.Size(200,40)
$btnAtualizar.FlatStyle = 'Flat'
$btnAtualizar.BackColor = $NeonRed
$btnAtualizar.ForeColor = 'White'
$form.Controls.Add($btnAtualizar)

# ================= EVENTOS =================
$btnConectar.Add_Click({
    try {
        $destino = $txtComp.Text.Trim()
        if (-not $destino) { return }

        if (-not (Test-Connection $destino -Count 1 -Quiet)) {
            throw "Host não encontrado"
        }

        if (Eh-IP $destino) {
            Garantir-TrustedHost $destino
        }

        Atualizar-Processos $destino
    } catch {
        [System.Windows.Forms.MessageBox]::Show($_.Exception.Message,"Erro")
    }
})

$btnAtualizar.Add_Click({
    if ($txtComp.Text) {
        Atualizar-Processos $txtComp.Text.Trim()
    }
})

$btnFinalizar.Add_Click({
    if (-not $lstProcessos.SelectedItem) { return }

    $destino = $txtComp.Text.Trim()
    $proc = ($lstProcessos.SelectedItem -split '\s+')[0]

    if (
        [System.Windows.Forms.MessageBox]::Show(
            "Finalizar processo '$proc'?",
            "Confirmação","YesNo","Warning"
        ) -eq "Yes"
    ) {
        Invoke-Command -ComputerName $destino -ScriptBlock {
            param($p) Stop-Process -Name $p -Force
        } -ArgumentList $proc

        Atualizar-Processos $destino
    }
})

[void]$form.ShowDialog()
