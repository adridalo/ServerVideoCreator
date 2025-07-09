@echo off
cd /d %~dp0
pyinstaller --debug=imports --onefile --name ServerVideoCreator main.py

copy ffmpeg.exe dist\
copy proxy.config.json dist\
