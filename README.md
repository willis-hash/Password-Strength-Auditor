# Password Strength Auditing System
**Student:** Willis Nyaramba | **Reg No:** 192196
**Course:** CNS 3104 | **Supervisor:** Mr. Tiberius Tabulu
**Institution:** Strathmore University, School of Computing and Engineering Sciences

---

## Project Overview
A Windows desktop application that evaluates password security through rule-based
analysis and real-world dictionary attack simulation using John the Ripper.
Built with Python, Tkinter, and PostgreSQL.

---

## System Requirements
- Windows 10/11
- Python 3.13+
- PostgreSQL 18+
- John the Ripper (Jumbo Community Edition, winX64)
- rockyou.txt wordlist

---

## Installation & Setup Guide

### 1. Clone the Repository
```bash
git clone https://github.com/willis-hash/Password-Strength-Auditor.git
cd Password-Strength-Auditor
```

### 2. Create and Activate Virtual Environment
```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install psycopg2-binary pyotp qrcode[pil] pillow bcrypt
```

### 4. Set Up PostgreSQL Database
Open psql and run:
```sql
CREATE DATABASE password_auditor;
\c password_auditor

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    totp_secret TEXT,
    is_2fa_enabled BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

CREATE TABLE sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    session_token TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    details TEXT,
    ip_address VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE password_audits (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    password_hash TEXT NOT NULL,
    strength_score INTEGER,
    strength_label VARCHAR(50),
    cracked_by_jtr BOOLEAN DEFAULT FALSE,
    audit_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 5. Configure the Application
Create a `config.py` file in the project root (this file is excluded from Git for security):
```python
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "password_auditor",
    "user": "postgres",
    "password": "YOUR_POSTGRES_PASSWORD"
}

APP_NAME = "Password Strength Auditor"
SESSION_EXPIRY_HOURS = 24

JOHN_PATH = r"C:\path\to\john.exe"
WORDLIST_PATH = r"C:\path\to\rockyou.txt"
```

### 6. Install John the Ripper
- Download Jumbo Community Edition from: https://www.openwall.com/john/
- Extract and note the path to `john.exe`
- Download `rockyou.txt` wordlist and place it in the JtR `run` folder
- Update `JOHN_PATH` and `WORDLIST_PATH` in `config.py`

### 7. Register a User & Enable 2FA
```bash
python enable-2fa.py
```
Scan the generated QR code with Google Authenticator.

### 8. Run the Application
```bash
python main.py
```

---

## Project Structure
password_auditor/

├── main.py                  # Entry point

├── config.py                # DB + JtR config (excluded from Git)

├── enable-2fa.py            # Utility: enable 2FA for a user

├── db/

│   └── database.py          # PostgreSQL connection

├── auth/

│   ├── login.py             # Registration + authentication (bcrypt)

│   ├── logout.py            # Session management

│   └── totp.py              # TOTP 2FA (pyotp + qrcode)

├── auditor/

│   ├── rule_engine.py       # Rule-based password analysis

│   ├── jtr_integration.py   # John the Ripper subprocess integration

│   └── scoring_engine.py    # Final scoring + feedback reconciliation

├── ui/

│   ├── login_screen.py      # Tkinter login window

│   ├── totp_screen.py       # Tkinter 2FA entry window

│   └── dashboard.py         # Tkinter main dashboard + audit UI

└── assets/

└── qr_codes/            # Generated QR code images (excluded from Git)
---

## System Architecture
The system follows a 4-layer architecture:
- **Presentation Layer** — Tkinter GUI (`ui/`)
- **Application Layer** — Password Analyser, Rule Engine, Attack Simulator, Suggestions Engine (`auditor/`)
- **Data Layer** — PostgreSQL database, rockyou.txt wordlist (`db/`)
- **Security Layer** — bcrypt hashing, TOTP 2FA, session management, temp file cleanup (`auth/`)

---

## Branching Strategy
| Branch | Purpose |
|---|---|
| `main` | Production-ready code |
| `development` | Active development branch |

---

## Cloning to a New Device
```bash
git clone https://github.com/willis-hash/Password-Strength-Auditor.git
cd Password-Strength-Auditor
python -m venv .venv
.venv\Scripts\activate
pip install psycopg2-binary pyotp qrcode[pil] pillow bcrypt
```
Then follow steps 4-8 above to configure PostgreSQL, JtR, and `config.py`.

---

## Security Notes
- `config.py` is excluded from version control — never commit database credentials
- All password cracking is performed locally on researcher-generated hashes only
- Temporary hash files are deleted automatically after each audit session
- Passwords are stored using bcrypt hashing with per-user salts