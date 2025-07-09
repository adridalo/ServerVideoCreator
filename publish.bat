@echo off
REM Force script to run from script's directory
cd /d %~dp0

pyinstaller --noconfirm --onefile --name ServerVideoCreator --paths=. main.py

copy ffmpeg.exe dist\
copy proxy.config.json dist\
