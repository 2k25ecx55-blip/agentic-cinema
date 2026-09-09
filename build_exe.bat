@echo off
echo Installing requirements...
pip install -r requirements.txt
pip install pyinstaller

echo.
echo Building the .exe file...
pyinstaller --noconsole --onefile gui_app.py

echo.
echo The build is complete! Your .exe is located in the "dist" folder.
pause
