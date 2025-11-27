import socket
import sys
import os
import json
import threading

# Ensure src is in python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from src.common.network import send_msg, recv_msg

SERVER_IP = '127.0.0.1'
SERVER_PORT = 5003

def watchman():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((SERVER_IP, SERVER_PORT))
        print("Connected to Testing Server (Watchman Mode)")

        # Identify as watchman
        send_msg(sock, {"type": "watchman_connect"})

        while True:
            msg = recv_msg(sock)
            if not msg:
                print("Server disconnected.")
                break

            msg_type = msg.get("type")

            if msg_type == "log_update":
                print("\n--- Current Logs ---")
                logs = msg.get("logs", [])
                print_table(logs)

            elif msg_type == "new_detection":
                print("\n!!! New Detection !!!")
                log = msg.get("log")
                print_row(log)

    except KeyboardInterrupt:
        print("Exiting...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        sock.close()

def print_table(logs):
    print(f"{'Type':<15} | {'Date':<12} | {'Time':<10} | {'Camera':<8} | {'Photo'}")
    print("-" * 70)
    for log in logs:
        print_row(log)

def print_row(log):
    print(f"{log['type']:<15} | {log['date']:<12} | {log['time']:<10} | {log['camera_id']:<8} | {log['photo']}")

if __name__ == "__main__":
    watchman()
