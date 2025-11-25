@echo off
echo Starting Multi-sistemas Cluster...

start "Training Server" cmd /k "cd src/training && python training_server.py"
timeout /t 2

start "Video Server" cmd /k "cd src/video_server && python video_server.py"
timeout /t 2

start "Testing Server" cmd /k "cd src/testing && python testing_server.py"
timeout /t 2

echo All servers started.
echo To start the client, run: cd src/monitoring && python vigilante_client.py
pause
