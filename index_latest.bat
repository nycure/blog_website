@echo off
call venv\Scripts\activate
set /p url="Enter the full URL of the new post to index: "
python index_now.py "%url%"
pause
