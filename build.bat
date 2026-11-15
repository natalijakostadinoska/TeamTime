@echo off
echo Building TeamTime (needs Python + Node.js)...
pip install psutil pillow pyinstaller
pyinstaller --onefile --noconsole --name TeamTimeAgent agent.py
call npm install
call npm run dist
echo.
echo Done! In the "dist" folder:
echo   TeamTimeAgent.exe   - give to teammates
echo   TeamTime Admin.exe  - your admin app
pause
