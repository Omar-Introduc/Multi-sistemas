import socket
import threading
import struct
import json
import time

class SocketConfig:
    HEADER_SIZE = 4  # 4 bytes for payload length
    ENCODING = 'utf-8'

class SocketMessage:
    def __init__(self, msg_type, payload):
        self.msg_type = msg_type
        self.payload = payload

    def to_bytes(self):
        # Protocol: Type (1 byte) | Length (4 bytes) | Payload
        # Actually, let's stick to a simpler JSON wrapper for control, and raw bytes for data if needed.
        # For now, let's send everything as a JSON string for simplicity in control messages,
        # but we might need raw bytes for images.
        # Hybrid approach: Header = Length (4 bytes big endian)
        # Body = JSON or Raw Bytes?
        # Let's use a JSON envelope.
        content = json.dumps({"type": self.msg_type, "data": self.payload}).encode(SocketConfig.ENCODING)
        length = len(content)
        return struct.pack('>I', length) + content

    @staticmethod
    def from_bytes(data):
        try:
            obj = json.loads(data.decode(SocketConfig.ENCODING))
            return SocketMessage(obj.get("type"), obj.get("data"))
        except Exception as e:
            print(f"Error parsing message: {e}")
            return None

def send_msg(sock, msg_type, data):
    msg = SocketMessage(msg_type, data)
    sock.sendall(msg.to_bytes())

def recv_msg(sock):
    # Read Header
    raw_len = recvall(sock, SocketConfig.HEADER_SIZE)
    if not raw_len:
        return None
    msg_len = struct.unpack('>I', raw_len)[0]
    # Read Body
    raw_data = recvall(sock, msg_len)
    if not raw_data:
        return None
    return SocketMessage.from_bytes(raw_data)

def recvall(sock, n):
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

class SocketServer:
    def __init__(self, host='0.0.0.0', port=5000):
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        self.clients = []

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.running = True
        print(f"Server listening on {self.host}:{self.port}")

        accept_thread = threading.Thread(target=self._accept_clients)
        accept_thread.start()

    def _accept_clients(self):
        while self.running:
            try:
                client_sock, addr = self.server_socket.accept()
                print(f"New connection from {addr}")
                self.clients.append(client_sock)
                client_handler = threading.Thread(target=self.handle_client, args=(client_sock,))
                client_handler.start()
            except OSError:
                break

    def handle_client(self, client_sock):
        # To be overridden or assigned by the specific server implementation
        try:
            while True:
                msg = recv_msg(client_sock)
                if not msg:
                    break
                print(f"Received: {msg.msg_type}")
                # Echo back for now or process
        except Exception as e:
            print(f"Client error: {e}")
        finally:
            print("Closing client connection")
            client_sock.close()
            if client_sock in self.clients:
                self.clients.remove(client_sock)

    def stop(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        for c in self.clients:
            c.close()

class SocketClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = None

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        print(f"Connected to {self.host}:{self.port}")

    def send(self, msg_type, data):
        if self.sock:
            send_msg(self.sock, msg_type, data)

    def receive(self):
        if self.sock:
            return recv_msg(self.sock)
        return None

    def close(self):
        if self.sock:
            self.sock.close()
