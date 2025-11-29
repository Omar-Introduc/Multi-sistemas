@echo off
echo Starting Testing Cluster (Video + Testing Server)...

start "Video Server" cmd /k "call .venv\Scripts\activate && cd src/video_server && python video_server.py"
timeout /t 2

start "Testing Server" cmd /k "call .venv\Scripts\activate && cd src/testing && python testing_server.py"
timeout /t 2

echo Testing Cluster started.
echo Now run the Vigilante Client manually:
echo cd src/monitoring
echo python vigilante_client.py
pause
