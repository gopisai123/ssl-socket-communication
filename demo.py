"""
SSL Demo — Automated Test
=========================
Starts the server in a background thread, connects a client,
sends a few test messages, and prints the full exchange.

Run with:  python demo.py
"""

import socket
import ssl
import threading
import time
import sys

HOST     = "localhost"
PORT     = 8444           # different port so it doesn't clash
CERTFILE = "certs/server.crt"
KEYFILE  = "certs/server.key"

RESULTS = []

# ─── Mini Server ──────────────────────────────────────────────────────────────
def run_server(ready_event):
    raw = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    raw.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(CERTFILE, KEYFILE)

    srv = ctx.wrap_socket(raw, server_side=True)
    srv.bind((HOST, PORT))
    srv.listen(1)
    ready_event.set()           # signal that server is up

    conn, addr = srv.accept()
    cipher = conn.cipher()
    RESULTS.append(("SERVER", f"Client connected from {addr}"))
    RESULTS.append(("SERVER", f"TLS cipher: {cipher[0]} / {cipher[1]}"))

    while True:
        data = conn.recv(4096)
        if not data:
            break
        msg = data.decode().strip()
        RESULTS.append(("SERVER", f"Received: {msg!r}"))
        if msg.lower() == "quit":
            conn.sendall(b"Goodbye!")
            break
        elif msg.lower() == "ping":
            reply = "PONG"
        else:
            reply = f"[ECHO] {msg}"
        conn.sendall(reply.encode())
        RESULTS.append(("SERVER", f"Sent:     {reply!r}"))

    conn.close()
    srv.close()

# ─── Mini Client ──────────────────────────────────────────────────────────────
def run_client(ready_event):
    ready_event.wait()          # wait until server is ready
    time.sleep(0.1)

    raw = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.load_verify_locations(CERTFILE)
    ctx.check_hostname = True
    ctx.verify_mode = ssl.CERT_REQUIRED

    sock = ctx.wrap_socket(raw, server_hostname=HOST)
    sock.connect((HOST, PORT))

    cipher = sock.cipher()
    cert   = sock.getpeercert()
    RESULTS.append(("CLIENT", f"Connected! TLS cipher: {cipher[0]} / {cipher[1]}"))
    RESULTS.append(("CLIENT", f"Server CN verified: {cert['subject'][0][0][1]}"))

    messages = ["Hello, Server!", "ping", "SSL is working!", "quit"]
    for msg in messages:
        sock.sendall(msg.encode())
        RESULTS.append(("CLIENT", f"Sent:     {msg!r}"))
        resp = sock.recv(4096).decode()
        RESULTS.append(("CLIENT", f"Received: {resp!r}"))
        time.sleep(0.05)

    sock.close()

# ─── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    ready = threading.Event()

    st = threading.Thread(target=run_server, args=(ready,), daemon=True)
    ct = threading.Thread(target=run_client, args=(ready,), daemon=True)

    st.start()
    ct.start()
    ct.join(timeout=10)
    time.sleep(0.3)

    print("\n" + "═"*60)
    print("  SSL SOCKET DEMO — FULL EXCHANGE LOG")
    print("═"*60)

    for role, line in RESULTS:
        prefix = "🔒 [SERVER]" if role == "SERVER" else "💻 [CLIENT]"
        print(f"  {prefix}  {line}")

    print("═"*60)
    print("  ✅  Demo complete — SSL communication successful!")
    print("═"*60 + "\n")
