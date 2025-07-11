pyinstaller --onefile --name ServerVideoCreator svc\main.py
copy ffmpeg.exe dist\
copy proxy.config.json dist\