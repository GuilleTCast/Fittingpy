<#
run_gui.ps1

Instala dependencias desde requirements.txt (si existe) y ejecuta la GUI
sin mostrar consola (usa pythonw del venv o del sistema cuando esté disponible).

Ejecución recomendada desde la carpeta del proyecto.
Si PowerShell bloquea scripts:
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
#>

# Mover al directorio del script para rutas relativas
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $scriptDir

Write-Output "[run_gui] Directorio: $scriptDir"

# Detectar virtualenv local (.venv, venv, env)
$venvDirs = @('.venv','venv','env')
$venvPath = $null
foreach ($d in $venvDirs) {
    $p = Join-Path $scriptDir $d
    if (Test-Path $p) { $venvPath = $p; break }
}

if ($venvPath) {
    Write-Output "[run_gui] Virtualenv detectado en: $venvPath"
    $venvPython = Join-Path $venvPath 'Scripts\python.exe'
    $venvPythonw = Join-Path $venvPath 'Scripts\pythonw.exe'
    $venvPip = $venvPython
} else {
    $venvPython = $null
    $venvPythonw = $null
    $venvPip = $null
}

function Install-Requirements {
    if (Test-Path 'requirements.txt') {
        Write-Output '[run_gui] Instalando dependencias desde requirements.txt...'

        # Preferir pip del virtualenv si existe
        if ($venvPip -and (Test-Path $venvPip)) {
            & $venvPip -m pip install -r requirements.txt
            return
        }

        if (Get-Command python -ErrorAction SilentlyContinue) {
            & python -m pip install -r requirements.txt
        } elseif (Get-Command py -ErrorAction SilentlyContinue) {
            & py -m pip install -r requirements.txt
        } elseif (Get-Command pythonw -ErrorAction SilentlyContinue) {
            & (Get-Command pythonw).Path -m pip install -r requirements.txt
        } else {
            Write-Error '[run_gui] No se encontró Python (python, py o pythonw). Instale Python.'
            exit 1
        }
    } else {
        Write-Output '[run_gui] No existe requirements.txt - se omite la instalación.'
    }
}

function Start-GuiHidden {
    # Buscar un entrypoint válido: Fitting_tool.py, main.py o gui.py
    $entrypoints = @('Fitting_tool.py','main.py','gui.py')
    $entry = $entrypoints | Where-Object { Test-Path $_ } | Select-Object -First 1
    if (-not $entry) {
        Write-Error "[run_gui] No se encontró ningún entrypoint (Fitting_tool.py/main.py/gui.py) en $scriptDir"
        exit 1
    }

    # Preferir pythonw del venv
    if ($venvPythonw -and (Test-Path $venvPythonw)) {
        Write-Output "[run_gui] Iniciando $entry con pythonw del venv: $venvPythonw"
        Start-Process -FilePath $venvPythonw -ArgumentList $entry -WorkingDirectory $scriptDir
        return
    }

    # Preferir python del venv (oculto)
    if ($venvPython -and (Test-Path $venvPython)) {
        Write-Output "[run_gui] Iniciando $entry con python del venv (ventana oculta): $venvPython"
        Start-Process -FilePath $venvPython -ArgumentList $entry -WorkingDirectory $scriptDir -WindowStyle Hidden
        return
    }

    # Fallback a ejecutables del sistema
    $pythonwCmd = Get-Command pythonw -ErrorAction SilentlyContinue
    if ($pythonwCmd) {
        $pythonw = $pythonwCmd.Path
        Write-Output "[run_gui] Iniciando $entry con pythonw del sistema: $pythonw"
        Start-Process -FilePath $pythonw -ArgumentList $entry -WorkingDirectory $scriptDir
        return
    }

    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCmd) {
        $python = $pythonCmd.Path
        Write-Output "[run_gui] Iniciando $entry con python del sistema (ventana oculta): $python"
        Start-Process -FilePath $python -ArgumentList $entry -WorkingDirectory $scriptDir -WindowStyle Hidden
        return
    }

    $pyCmd = Get-Command py -ErrorAction SilentlyContinue
    if ($pyCmd) {
        $py = $pyCmd.Path
        Write-Output "[run_gui] Iniciando $entry con py del sistema (ventana oculta): $py"
        Start-Process -FilePath $py -ArgumentList '-3', $entry -WorkingDirectory $scriptDir -WindowStyle Hidden
        return
    }

    Write-Error '[run_gui] No se encontró ningún ejecutable de Python para iniciar la aplicación'
    exit 1
}

# --- Ejecución ---
Install-Requirements
Start-GuiHidden

Write-Output '[run_gui] Proceso lanzado. Este script puede terminar ahora.'
