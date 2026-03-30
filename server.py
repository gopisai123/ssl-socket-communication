"""
SSL Socket Server
=================
A simple SSL/TLS encrypted server that listens for client connections,
receives messages, and sends back encrypted responses.

Usage:
    python server.py

The server listens on localhost:8443 by default.
"""

import socket
import ssl
import threading
import datetime

# ─── Configuration ────────────────────────────────────────────────────────────
HOST = "localhost"
PORT = 8443
CERTFILE = "certs/server.crt"   # Self-signed certificate
KEYFILE  = "certs/server.key"   # Private key


def log(tag, msg):
    """Pretty-print a log message with timestamp."""
    now = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] [{tag}] {msg}")


def handle_client(conn, addr):
    """Handle a single SSL client connection in its own thread."""
    log("CONNECT", f"New client connected from {addr}")

    # Show TLS details
    cipher = conn.cipher()
    log("TLS", f"Cipher: {cipher[0]}  Protocol: {cipher[1]}")

    try:
        while True:
            # Receive data (up to 4096 bytes)
            data = conn.recv(4096)
            if not data:
                break  # Client disconnected

            message = data.decode("utf-8").strip()
            log("RECV", f"From {addr}: {message!r}")

            # Build a response
            if message.lower() == "quit":
                response = "Goodbye! Closing connection."
                conn.sendall(response.encode("utf-8"))
                break
            elif message.lower() == "ping":
                response = "PONG"
            else:
                response = f"[SERVER ECHO] {message}"

            conn.sendall(response.encode("utf-8"))
            log("SEND", f"To {addr}: {response!r}")

    except ssl.SSLError as e:
        log("SSL-ERROR", str(e))
    except ConnectionResetError:
        log("DISCONNECT", f"{addr} reset the connection")
    finally:
        conn.close()
        log("CLOSE", f"Connection with {addr} closed")


def main():
    # ── Step 1: Create a plain TCP socket ─────────────────────────────────────
    raw_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    raw_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # ── Step 2: Create an SSL context ─────────────────────────────────────────
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

    # Load the server certificate and private key
    context.load_cert_chain(certfile=CERTFILE, keyfile=KEYFILE)

    # ── Step 3: Wrap the socket with SSL ──────────────────────────────────────
    ssl_sock = context.wrap_socket(raw_sock, server_side=True)

    # ── Step 4: Bind and listen ───────────────────────────────────────────────
    ssl_sock.bind((HOST, PORT))
    ssl_sock.listen(5)
    log("START", f"SSL Server listening on {HOST}:{PORT}")
    log("INFO", "Waiting for encrypted connections... (Ctrl+C to stop)")

    try:
        while True:
            # Accept an incoming connection (already SSL-wrapped)
            conn, addr = ssl_sock.accept()
            # Spawn a thread per client so we can handle multiple clients
            t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            t.start()
    except KeyboardInterrupt:
        log("STOP", "Server shutting down.")
    finally:
        ssl_sock.close()


if __name__ == "__main__":
    main()
