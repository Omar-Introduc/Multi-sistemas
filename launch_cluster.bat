@echo off
echo Starting Multi-sistemas Cluster...

start "Training Server" cmd /k "call .venv\Scripts\activate && cd src/training && python training_server.py"
timeout /t 2

start "Worker 1" cmd /k "call .venv\Scripts\activate && cd src/training && python worker_server.py 6000"
start "Worker 2" cmd /k "call .venv\Scripts\activate && cd src/training && python worker_server.py 6001"
start "Worker 3" cmd /k "call .venv\Scripts\activate && cd src/training && python worker_server.py 6002"
timeout /t 2

start "Video Server" cmd /k "call .venv\Scripts\activate && cd src/video_server && python video_server.py"
timeout /t 2

start "Testing Server" cmd /k "call .venv\Scripts\activate && cd src/testing && python testing_server.py"
timeout /t 2

echo All servers started.
echo To start the client, run: cd src/monitoring ^&^& python vigilante_client.py
pause
