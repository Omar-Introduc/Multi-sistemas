import subprocess
import time
import os
import sys
import argparse

def run_train():
    print("\n[Phase: TRAIN] Launching Training Cluster...")
    # Start Training Cluster
    subprocess.Popen(["cmd", "/c", "launch_training_only.bat"], creationflags=subprocess.CREATE_NEW_CONSOLE)
    time.sleep(5) # Wait for servers
    
    print("Running Distributed Clients...")
    clients = []
    for i in range(3):
        cmd = f"call .venv\\Scripts\\activate && python src/training/train_client.py datasets --shard_id {i} --num_shards 3"
        print(f"  -> Starting Client {i+1}...")
        p = subprocess.Popen(cmd, shell=True)
        clients.append(p)
    
    for p in clients:
        p.wait()
    print("Training Clients Finished.")

def run_evaluate():
    print("\n[Phase: EVALUATE] Evaluating Model...")
    subprocess.run("call .venv\\Scripts\\activate && python src/training/evaluate_model.py", shell=True, check=True)
    
    print("Generating Plots...")
    subprocess.run("call .venv\\Scripts\\activate && python src/training/plot_results.py", shell=True, check=True)

def run_test():
    print("\n[Phase: TEST] Launching Testing Cluster (Real Test)...")
    subprocess.Popen(["cmd", "/c", "launch_testing_only.bat"], creationflags=subprocess.CREATE_NEW_CONSOLE)
    time.sleep(5)
    
    print("Launching Vigilante Client...")
    os.system("start cmd /k \"call .venv\\Scripts\\activate && cd src/monitoring && python vigilante_client.py\"")

def run_kill():
    print("\n[Phase: KILL] Stopping all Python processes...")
    subprocess.run("taskkill /F /IM python.exe", shell=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Automate Multi-sistemas Pipeline')
    parser.add_argument('phase', choices=['train', 'evaluate', 'test', 'kill', 'all'], help='Phase to run')
    args = parser.parse_args()
    
    if args.phase == 'kill':
        run_kill()
    elif args.phase == 'train':
        run_train()
    elif args.phase == 'evaluate':
        run_evaluate()
    elif args.phase == 'test':
        run_test()
    elif args.phase == 'all':
        run_kill()
        run_train()
        run_evaluate()
        run_kill()
        run_test()

