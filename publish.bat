pyinstaller --noconfirm --onefile --name ServerVideoCreator main.py
copy ffmpeg.exe dist\
copy proxy.config.json dist\