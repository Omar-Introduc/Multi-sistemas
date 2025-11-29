@echo off
echo Starting Distributed Training Simulation...
echo Assuming Dataset is in "datasets" folder.

:: Launch 3 Clients in parallel
:: Each client takes 1/3 of the dataset and sends it to the server

start "Client 1 (Shard 1/3)" cmd /k "call .venv\Scripts\activate && python src/training/train_client.py datasets --shard_id 0 --num_shards 3"
start "Client 2 (Shard 2/3)" cmd /k "call .venv\Scripts\activate && python src/training/train_client.py datasets --shard_id 1 --num_shards 3"
start "Client 3 (Shard 3/3)" cmd /k "call .venv\Scripts\activate && python src/training/train_client.py datasets --shard_id 2 --num_shards 3"

echo 3 Clients launched. Check Training Server console for activity.
pause
