import socket
import requests
import threading
from datetime import datetime
from urllib.parse import urlparse

# Server bind configuration
HOST = '0.0.0.0'
PORT = 5050
ADDR = (HOST, PORT)
cache = {}
forbidden_domains = ['example.com', 'google.com', 'facebook.com']
DEFAULT_CACHE_DURATION = 10  # Default cache duration in seconds

def fetch_web_content(url):
    try:
        response = requests.get(url, timeout=15)
        cache_control = response.headers.get('Cache-Control', '')
        cache_duration = extract_max_age(cache_control) if 'max-age' in cache_control else DEFAULT_CACHE_DURATION
        return response.content, cache_duration
    except requests.exceptions.ConnectTimeout:
        print(f"[ERROR] Timeout while trying to connect to {url}")
        return None, DEFAULT_CACHE_DURATION
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Error fetching data from {url}: {e}")
        return None, DEFAULT_CACHE_DURATION

def extract_max_age(cache_control):
    # Extract max-age from Cache-Control
    seqments = dict(seqment.strip().split('=') for seqment in cache_control.split(',') if '=' in seqment)
    return int(seqments['max-age']) if 'max-age' in seqments else DEFAULT_CACHE_DURATION

def serve_client(client_conn):
    try:
     request = client_conn.recv(4096).decode()

     print(f"[NEW REQUEST] New request received from port {client_conn.getpeername()[1]}")

     # Parse request line and headers
     request_lines = request.split('\n')
     first_line = request_lines[0].strip()
     
     headers = {}
     for line in request_lines[1:]:
        if ':' in line:
            key, value = line.split(':', 1)
            headers[key.strip()] = value.strip()
            
     host = headers.get('Host')

     try:
        _, path, _ = first_line.split(' ')
     except ValueError:
        print("[ERROR] Malformed request line.")
        return

     if not host:
         response = "HTTP/1.1 400 Bad Request\r\n\r\nMissing Host header"
         client_conn.sendall(response.encode())
         return

     url = f"http://{host}{path}"

     # Firewall: block requests whose host matches a forbidden domain
     try:
        requested_host = urlparse(url).netloc.lower()
     except Exception:
        requested_host = host.lower()

     if requested_host in forbidden_domains:
         response = "HTTP/1.1 403 Forbidden\r\n\r\nBlocked by firewall: Access to requested domain is forbidden."
         client_conn.sendall(response.encode())
         print(f"[FORBIDDEN] Access to {url} is blocked.")
         return

     # Cache check: serve if present and not expired
     if url in cache and (datetime.now() - cache[url]['timestamp']).seconds < cache[url]['max_age']:
         data_response = cache[url]['data']
         cache_status = "HIT"
         cache_duration = cache[url]['max_age']
         print(f"[CACHE HIT] Serving {url} from cache.")
     else:
         # Fetch from origin and store in cache if successful
         data_response, cache_duration = fetch_web_content(url)
         if data_response:
             cache[url] = {'data': data_response, 'max_age': cache_duration, 'timestamp': datetime.now()}
             cache_status = "MISS"
             print(f"[CACHE MISS] Fetched {url} from origin and cached.")

         # 502 Bad Gateway if origin fetch fails
     if data_response is None:
         err_msg = f"[ERROR] Failed to fetch {url}"
         response = f"HTTP/1.1 502 Bad Gateway\r\nContent-Length: {len(err_msg)}\r\n\r\n{err_msg}"
         client_conn.sendall(response.encode())
         return

        # Send payload back to client
     response_headers = f"CacheStatus: {cache_status}\r\nCache-Control: max-age={cache_duration}\r\n"
     response = (f"HTTP/1.1 200 OK\r\n{response_headers}\r\n").encode() + data_response
     client_conn.sendall(response)

    except Exception as e:
        print(f"[ERROR] Error during request: {e}")
        response = "HTTP/1.1 500 Internal Server Error\r\n\r\n"
        client_conn.sendall(response.encode())
    finally:
        client_conn.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind(ADDR)
    except socket.error as e:
        print(f"[ERROR] Could not bind to {ADDR}: {e}")
        return
        
    server.listen()
    print(f"[LISTENING] proxy server listening on port {PORT}")

    while True:             
        # A TCP three-way handshake is made when a new connection is accepted
        try:
            connection, address = server.accept()
            print(f"\n[NEW CONNECTION] Accepted connection from {address}")
            # threading to serve client concurrently
            thread = threading.Thread(target=serve_client, args=(connection,))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
        except Exception as e:
            print(f"[ERROR] Server accept failed: {e}")
            break

start_server()