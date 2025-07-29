 # 检查虚拟环境是否存在
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv .venv
}

# 激活虚拟环境
if ($PSVersionTable.Platform -eq 'Unix') {
    & .venv/bin/Activate.ps1
} else {
    & .venv\Scripts\Activate.ps1
}

# 检查依赖是否已安装
$uvicornPath = if ($PSVersionTable.Platform -eq 'Unix') { ".venv/bin/uvicorn" } else { ".venv\Scripts\uvicorn.exe" }
if (-not (Test-Path $uvicornPath)) {
    Write-Host "Installing dependencies..."
    pip install -r requirements.txt
}

# 启动应用
Write-Host "Starting application..."
python -m uvicorn src.backend.main:app --reload

# 捕获 Ctrl+C 信号
try {
    Wait-Event
} finally {
    deactivate
}