"""
Simple UDP Client
"""

import socket

TARGET_HOST = "127.0.0.1"
TARGET_PORT = 9007

# create a socket object
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# send some data
client.sendto(b'AAABBBCCC', (TARGET_HOST, TARGET_PORT))

# receive some data
data, addr = client.recvfrom(4096)

print(data.decode())
client.close()
