import socket
import time
from urllib.parse import urlparse

HOST = socket.gethostbyname(socket.gethostname())
PORT = 5050
ADDR = (HOST, PORT)

def handle_request(url):
    # Create a TCP/IP socket
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    timer = time.time()

    urlParts = urlparse(url)
    requestPath = urlParts.path

    # Connect the socket to the server's address and port
    client.connect(ADDR)

    # Send an HTTP GET request to the server
    request = f"GET {requestPath} HTTP/1.1\r\nHost: {urlParts.netloc}\r\n\r\n"
    client.sendall(request.encode())

    # Receive the server's response
    response = b""
    while True:
        received_data = client.recv(4096)
        if not received_data:
            break
        response += received_data

    timer = (time.time() - timer) * 1000

    response_text = response.decode('utf-8')
    headers , _ , _ = response_text.partition('\r\n\r\n')

    print(f"Time taken: {timer:.2f} ms")
    print("Headers:\n" + headers)


while True:
    user_request = input("\n\nEnter the url: ")
    handle_request(user_request)