@echo off
REM Make sure we're in the script directory
cd /d %~dp0

REM Show current directory
echo Building in %CD%

REM Compile with explicit path
pyinstaller --noconfirm --onefile --name ServerVideoCreator --paths=%CD% main.py

REM Copy additional files
copy ffmpeg.exe dist\
copy proxy.config.json dist\