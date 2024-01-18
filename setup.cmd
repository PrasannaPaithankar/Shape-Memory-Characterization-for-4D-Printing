@echo off
setlocal enabledelayedexpansion

rem Check if Python is installed
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python is not installed. Installing...
    
    rem Download and install Python
    set "pythonInstallerUrl=https://www.python.org/ftp/python/3.12.1/python-3.12.1-amd64.exe"
    set "pythonInstallerPath=%TEMP%\python-3.12.1-amd64.exe"
    
    bitsadmin /transfer "PythonInstaller" %pythonInstallerUrl% %pythonInstallerPath%
    
    echo Installing Python...
    start /wait %pythonInstallerPath% /quiet PrependPath=1
    
    echo Cleaning up...
    del %pythonInstallerPath%
    
    echo Python installation complete.
) else (
    echo Python is already installed.
)

rem create %USERPROFILE%\SMC4D if it doesn't exist
if not exist "%USERPROFILE%\SMC4D" (
    mkdir "%USERPROFILE%\SMC4D"
)
cd "%USERPROFILE%\SMC4D"
curl -OL https://github.com/PrasannaPaithankar/Shape-Memory-Characterization-for-4D-Printing/archive/master.zip
tar -xf master.zip
cd Shape-Memory-Characterization-for-4D-Printing-main
pip -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
pyinstaller --onefile --windowed --name=SMC4D angleGUI.py
move dist\SMC4D.exe ..
powershell -Command "(New-Object -COM WScript.Shell).CreateShortcut('%USERPROFILE%\Desktop\SMC4D.lnk').TargetPath = '%USERPROFILE%\SMC4D\SMC4D.exe'"
cd ..
del master.zip
endlocal