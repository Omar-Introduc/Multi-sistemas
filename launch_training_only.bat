@echo off
echo Starting Training Cluster (Master + 3 Workers)...

start "Training Server" cmd /k "call .venv\Scripts\activate && cd src/training && python training_server.py"
timeout /t 2

start "Worker 1" cmd /k "call .venv\Scripts\activate && cd src/training && python worker_server.py 6000"
start "Worker 2" cmd /k "call .venv\Scripts\activate && cd src/training && python worker_server.py 6001"
start "Worker 3" cmd /k "call .venv\Scripts\activate && cd src/training && python worker_server.py 6002"

echo Training Cluster started.
echo Now run simulate_distributed_training.bat to start training.
pause
