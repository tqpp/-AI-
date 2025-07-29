@echo off
setlocal

:: 检查虚拟环境是否存在
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

:: 激活虚拟环境
call .venv\Scripts\activate.bat

:: 检查依赖是否已安装
if not exist ".venv\Scripts\uvicorn.exe" (
    echo Installing dependencies...
    pip install -r requirements.txt
)

:: 启动应用
echo Starting application...
python -m uvicorn src.backend.main:app --reload

:: 退出时停用虚拟环境
deactivate
endlocal