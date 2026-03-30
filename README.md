# SSL Socket Communication

A simple client-server application demonstrating **SSL/TLS encrypted socket communication** using Python's built-in `ssl` module. All messages are encrypted end-to-end using TLS 1.3 with AES-256-GCM-SHA384.

---

## What This Project Does

When you type a message on the client, it does **not** travel as plain text. It is encrypted into unreadable ciphertext before leaving your machine, travels securely over the network, and is decrypted only when it reaches the server — and the same happens in reverse for replies.

```
Client  →  encrypts with session key  →  [gibberish on wire]  →  server decrypts  →  plain text
Server  →  encrypts reply             →  [gibberish on wire]  →  client decrypts  →  plain text
```

---

## Project Structure

```
SSL-Socket_Communication/
│
├── certs/
│   ├── server.crt        # Self-signed certificate (public — shared with client)
│   └── server.key        # Private key (secret — never leaves the server)
│
├── server.py             # SSL server — listens on localhost:8443
├── client.py             # SSL client — connects and sends messages interactively
├── demo.py               # Automated demo — runs both and shows full exchange
└── generate_cert.py      # One-time script to generate SSL certificates
```

---

## How SSL Works Here

### 1. Certificates
| File | Role |
|---|---|
| `server.crt` | The server's identity card — contains the public key. Shared with the client so it can verify the server. |
| `server.key` | The server's private key — used to prove it owns the certificate. Never shared. |

### 2. The Handshake (before any message is sent)
```
Client                                        Server
  |── "I want TLS 1.3" + random_C ──────────>  |
  |                                             |
  |<── certificate + random_S + signature ────  |
  |                                             |
  | Client checks:                              |
  |   ✓ Does cert match the one I trust?        |
  |   ✓ Is CN = "localhost"?                    |
  |   ✓ Is the signature valid?                 |
  |                                             |
  | Both sides derive the same session key      |
  | from random_C + random_S (key never sent!)  |
  |                                             |
  |<════ All messages now encrypted ═══════════>|
```

### 3. Why a Hacker Cannot Intercept
- The certificate is public — a hacker can copy it
- But the client also challenges: *"sign this random number with your private key"*
- Without `server.key`, the hacker **cannot produce a valid signature**
- The client detects this and refuses the connection

---

## Getting Started

### Prerequisites
- Python 3.8 or higher
- `cryptography` library (only needed to generate certs)

### Step 1 — Install dependency
```bash
pip install cryptography
```

### Step 2 — Generate SSL certificates (run once)
```bash
python generate_cert.py
```
This creates `certs/server.crt` and `certs/server.key`.

### Step 3 — Start the server
```bash
python server.py
```
```
[10:07:49] [START] SSL Server listening on localhost:8443
[10:07:49] [INFO]  Waiting for encrypted connections... (Ctrl+C to stop)
```

### Step 4 — Connect with the client (open a new terminal)
```bash
python client.py
```
```
[10:07:53] [CONNECT] SSL handshake complete!
[10:07:53] [TLS]     Cipher: TLS_AES_256_GCM_SHA384  Protocol: TLSv1.3
[10:07:53] [TLS]     Server CN: localhost

──────────────────────────────────────────
  Connected! Type a message and press Enter.
  Special commands: ping | quit
──────────────────────────────────────────

You: Hello!
Server: [SERVER ECHO] Hello!
```

### Step 5 — Run the automated demo (optional)
```bash
python demo.py
```
This starts both server and client automatically and shows the full encrypted exchange.

---

## Special Commands

| Command | Response |
|---|---|
| `ping` | Server replies `PONG` |
| `quit` | Server replies `Goodbye!` and closes the connection |
| Any other text | Server echoes back `[SERVER ECHO] your message` |

---

## Example Output

**Server terminal:**
```
[10:07:49] [START]   SSL Server listening on localhost:8443
[10:07:53] [CONNECT] New client connected from ('127.0.0.1', 59740)
[10:07:53] [TLS]     Cipher: TLS_AES_256_GCM_SHA384  Protocol: TLSv1.3
[10:08:02] [RECV]    From ('127.0.0.1', 59740): 'Hello! My name is Gopi Sai'
[10:08:02] [SEND]    To ('127.0.0.1', 59740): '[SERVER ECHO] Hello! My name is Gopi Sai'
```

**Client terminal:**
```
[10:07:53] [CONNECT] Connecting to localhost:8443 ...
[10:07:53] [CONNECT] SSL handshake complete!
[10:07:53] [TLS]     Cipher: TLS_AES_256_GCM_SHA384  Protocol: TLSv1.3
[10:07:53] [TLS]     Server CN: localhost

You: Hello! My name is Gopi Sai
[10:08:02] [SEND]    Sent: 'Hello! My name is Gopi Sai'
[10:08:02] [RECV]    Server says: '[SERVER ECHO] Hello! My name is Gopi Sai'
Server: [SERVER ECHO] Hello! My name is Gopi Sai
```

---

## Key Concepts Demonstrated

- **TLS 1.3 handshake** — identity verification before any data is exchanged
- **Certificate verification** — client checks server identity using `server.crt`
- **Private key challenge** — server proves ownership by signing a random value
- **Session key derivation** — both sides independently compute the same encryption key; it is never sent over the wire
- **AES-256-GCM encryption** — all messages encrypted in transit
- **Multi-client support** — server spawns a new thread per client connection

---

## Technologies Used

- **Python 3** — core language
- **ssl** — Python's built-in SSL/TLS module
- **socket** — low-level network communication
- **threading** — concurrent client handling
- **cryptography** — certificate generation (one-time setup only)

---

## Notes

- The certificate is **self-signed** — suitable for learning and local development
- In production, use a certificate from a trusted Certificate Authority (CA) like Let's Encrypt
- `server.key` should never be committed to version control — add it to `.gitignore` in real projects
