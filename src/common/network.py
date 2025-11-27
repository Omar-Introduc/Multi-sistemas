import socket
import struct
import json
import numpy as np
import cv2
import sys

def send_msg(sock, msg):
    """
    Sends a JSON message prefixed with its 4-byte length.
    """
    msg_json = json.dumps(msg)
    msg_bytes = msg_json.encode('utf-8')
    # Pack the length of the message as a 4-byte big-endian integer
    sock.sendall(struct.pack('>I', len(msg_bytes)) + msg_bytes)

def recv_msg(sock):
    """
    Receives a JSON message prefixed with its 4-byte length.
    """
    # Read message length
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    # Read the message data
    data = recvall(sock, msglen)
    if not data:
        return None
    return json.loads(data.decode('utf-8'))

def send_image(sock, image, meta_data=None):
    """
    Sends an image (numpy array) and optional metadata.
    Format:
    [4 bytes metadata length] [metadata json bytes]
    [4 bytes image size] [image bytes (jpg encoded)]
    """
    # Encode image to jpg to reduce size
    _, img_encoded = cv2.imencode('.jpg', image)
    img_bytes = img_encoded.tobytes()

    # Metadata
    meta = meta_data if meta_data else {}
    meta_json = json.dumps(meta)
    meta_bytes = meta_json.encode('utf-8')

    # Send metadata length
    sock.sendall(struct.pack('>I', len(meta_bytes)))
    # Send metadata
    sock.sendall(meta_bytes)

    # Send image size
    sock.sendall(struct.pack('>I', len(img_bytes)))
    # Send image data
    sock.sendall(img_bytes)

def recv_image(sock):
    """
    Receives an image and metadata.
    Returns (image, metadata)
    """
    # Read metadata length
    raw_meta_len = recvall(sock, 4)
    if not raw_meta_len:
        return None, None
    meta_len = struct.unpack('>I', raw_meta_len)[0]

    # Read metadata
    meta_data_bytes = recvall(sock, meta_len)
    if not meta_data_bytes:
        return None, None
    metadata = json.loads(meta_data_bytes.decode('utf-8'))

    # Read image size
    raw_img_len = recvall(sock, 4)
    if not raw_img_len:
        return None, None
    img_len = struct.unpack('>I', raw_img_len)[0]

    # Read image data
    img_bytes = recvall(sock, img_len)
    if not img_bytes:
        return None, None

    # Decode image
    nparr = np.frombuffer(img_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    return image, metadata

def recvall(sock, n):
    """
    Helper function to recv n bytes or return None if EOF is hit
    """
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data
