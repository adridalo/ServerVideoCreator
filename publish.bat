@echo off

set PYTHONPATH=%CD%
pyinstaller --noconfirm --onefile --name ServerVideoCreator --paths=%CD% main.py
copy ffmpeg.exe dist\
copy proxy.config.json dist\