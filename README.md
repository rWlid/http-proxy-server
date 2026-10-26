# Multithreaded HTTP Proxy Server with Caching & Firewall

Built in Python using raw sockets. The architecture consists of a multithreaded server acting as an intermediary for web requests, optimizing performance through custom in-memory caching and enforcing security constraints using domain-blocking firewall, alongside a CLI client.

> 🎓 **Academic Context:** Developed as a practical project for the **IS 370: Computer Networks and Data Communications** course within the Information Systems Department at King Saud University.

## 📁 Project Structure

*   `proxy_server.py`: The core multithreaded server handling firewall logic, caching, and forwarding requests to origin servers.
*   `proxy_client.py`: A command-line interface (CLI) client used to send HTTP requests through the proxy and benchmark response headers and round-trip time (RTT).

## 🌟 Key Features

*   **Concurrent Request Handling:** Deploys Python's `threading` module to accept and serve multiple client connections concurrently without blocking.
*   **Custom In-Memory Caching (TTL Support):** Implements an efficient caching mechanism that stores web content dynamically and respects `Cache-Control: max-age` headers for Time-To-Live (TTL) expiry.
*   **Domain-Blocking Firewall:** Enforces network security by intercepting and rejecting HTTP requests targeted at unauthorized or forbidden domains (e.g., `google.com`, `facebook.com`).
*   **Detailed Network Logging:** Provides real-time server console logs tracking system metrics including Cache Hits/Misses, Active Connections, and connection timeouts.

## 🛠️ Tech Stack & Concepts

*   **Language:** Python 3
*   **Network Layer:** Raw TCP/IP Sockets (`socket` module)
*   **Concurrency:** Multithreading (`threading` module)
*   **Concepts Applied:** HTTP/1.1 Protocol Parsing, Byte-stream manipulation, Network Security, Performance Optimization.

## 🚀 How to Run (Execution Guide)

To test the system locally, you need to execute the server and the client in **two separate terminal windows**:

### Step 1: Start the Proxy Server
Open your first terminal, navigate to the project directory, and run the server script. It will start listening for connections:
```bash
python3 proxy_server.py
```

### Step 2: Run the CLI Client
Open a second, separate terminal window, navigate to the same project directory, and run the client script:
```bash
python3 proxy_client.py
```

### Step 3: Test the System
In the client terminal, enter any destination URL when prompted (e.g., `http://example.com`). 
*   The **Client Terminal** will display the round-trip time (RTT) and parsed HTTP headers.
*   The **Server Terminal** will display live logs showing whether the request resulted in a `CACHE HIT`, a `CACHE MISS`, or was blocked by the `FIREWALL`.

## 📝 Future Improvements
*   Support for HTTPS (SSL/TLS).
*   Persistent storage for large cached items.
