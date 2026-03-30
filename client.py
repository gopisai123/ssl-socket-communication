"""
SSL Socket Client
=================
A simple SSL/TLS encrypted client that connects to the SSL server,
sends messages, and receives encrypted responses.

Usage:
    python client.py

Type any message and press Enter to send. Type 'quit' to exit.
"""

import socket
import ssl
import datetime

# ─── Configuration ────────────────────────────────────────────────────────────
HOST     = "localhost"
PORT     = 8443
CERTFILE = "certs/server.crt"   # Used to verify the server's certificate


def log(tag, msg):
    """Pretty-print a log message with timestamp."""
    now = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] [{tag}] {msg}")


def main():
    # ── Step 1: Create a plain TCP socket ─────────────────────────────────────
    raw_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # ── Step 2: Create an SSL context ─────────────────────────────────────────
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)

    # Load the server's certificate to verify its identity (prevents MITM)
    context.load_verify_locations(CERTFILE)

    # Enforce hostname checking
    context.check_hostname = True
    context.verify_mode = ssl.CERT_REQUIRED

    # ── Step 3: Wrap the socket with SSL ──────────────────────────────────────
    ssl_sock = context.wrap_socket(raw_sock, server_hostname=HOST)

    try:
        # ── Step 4: Connect to the server ─────────────────────────────────────
        log("CONNECT", f"Connecting to {HOST}:{PORT} ...")
        ssl_sock.connect((HOST, PORT))
        log("CONNECT", "SSL handshake complete!")

        # Show TLS details
        cipher = ssl_sock.cipher()
        cert   = ssl_sock.getpeercert()
        log("TLS", f"Cipher: {cipher[0]}  Protocol: {cipher[1]}")
        log("TLS", f"Server CN: {cert['subject'][0][0][1]}")

        print("\n" + "─" * 50)
        print("  Connected! Type a message and press Enter.")
        print("  Special commands: ping | quit")
        print("─" * 50 + "\n")

        # ── Step 5: Interactive send/receive loop ─────────────────────────────
        while True:
            try:
                message = input("You: ").strip()
            except EOFError:
                break

            if not message:
                continue

            # Send the message
            ssl_sock.sendall(message.encode("utf-8"))
            log("SEND", f"Sent: {message!r}")

            # Receive the server's response
            data = ssl_sock.recv(4096)
            if not data:
                log("INFO", "Server closed the connection.")
                break

            response = data.decode("utf-8")
            log("RECV", f"Server says: {response!r}")
            print(f"Server: {response}\n")

            if message.lower() == "quit":
                break

    except ssl.SSLCertVerificationError as e:
        log("SSL-ERROR", f"Certificate verification failed: {e}")
        log("HINT", "Make sure certs/server.crt matches the server's certificate.")
    except ConnectionRefusedError:
        log("ERROR", f"Connection refused. Is the server running on port {PORT}?")
    except ssl.SSLError as e:
        log("SSL-ERROR", str(e))
    finally:
        ssl_sock.close()
        log("CLOSE", "Connection closed.")


if __name__ == "__main__":
    main()
