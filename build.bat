@echo off
setlocal

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not added to PATH
    echo [INFO] Opening the official Python download page...
    start https://www.python.org/downloads/
    pause
    exit /b 1
)

py -m venv .venv
call .venv\Scripts\activate

:: Get proxy from JSON file
for /f "delims=" %%p in ('python -c "import json; print(json.load(open('proxy.config.json'))['proxy'])"') do set PROXY=%%p

:: Install w/ proxy

:: Step 1: Upgrade pip inside the virtual environment
echo [INFO] Upgrading pip in the virtual environment...
pip install --upgrade pip --proxy %PROXY%
echo [INFO] pip upgraded successfully.

:: Step 2: Upgrade all installed packages inside the virtual environment
echo [INFO] Upgrading all installed packages in the virtual environment...
for /f "delims=" %%a in ('pip freeze') do (
    pip install --upgrade %%a --proxy %PROXY%
)
echo [INFO] All packages upgraded successfully.

:: Step 3: Update requirements.txt with the latest versions inside the virtual environment
echo [INFO] Updating requirements.txt with the latest versions...
pip freeze > requirements.txt --proxy %PROXY%
echo [INFO] requirements.txt updated successfully.

:: Step 4: Update new packages saved in requirements.txt
echo [INFO] Updating packges saved in requirements.txt
pip install -r requirements.txt --proxy %PROXY%
echo [INFO] pip packges updated successfully.


:: Finish
echo [INFO] Update process completed successfully!

cls

echo [INFO] Build installed successfully!