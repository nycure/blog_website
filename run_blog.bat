@echo off
REM Check if venv exists
if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment not found. Setting it up...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

python auto_blog.py
pause
