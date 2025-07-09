@echo off
REM Make sure we are in the directory where publish.bat lives
cd /d %~dp0

set PYTHONPATH=%CD%
pyinstaller --noconfirm --onefile --name ServerVideoCreator --paths=%CD% main.py
copy ffmpeg.exe dist\
copy proxy.config.json dist\
