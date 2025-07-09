@echo off
cd /d %~dp0
pyinstaller ServerVideoCreator.spec
copy ffmpeg.exe dist\
copy proxy.config.json dist\
