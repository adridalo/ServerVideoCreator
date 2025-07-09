@echo off
REM Force script to run from script's directory
cd /d %~dp0

pyinstaller ServerVideoCreator.spec
