# UPOSD (Universal Portable Offensive Security Device)

UPOSD (Universal Portable Offensive Security Device) is a full-stack Flask-based enterprise cybersecurity dashboard built for academic demonstration. It simulates offensive security workflows in **safe demo mode** and provides real-time monitoring UX with a modern dark cyber theme.

## Features

- Flask + SQLite modular backend
- Flask-Login authentication (default admin account)
- REST APIs for dashboard metrics, scan control, device discovery, alerts, reports
- Network scanning integration path (`nmap -sn`) with safe fallback simulation
- Vulnerability and threat analytics dashboards
- IoT/device monitoring simulation
- Live terminal-style activity feed and Chart.js visual analytics
- Report download as CSV
- Raspberry Pi friendly lightweight deployment

## Project Structure

```text
UPOSD/
├── app.py
├── requirements.txt
├── uposd/
│   ├── __init__.py
│   ├── auth.py
│   ├── main.py
│   ├── models.py
│   ├── scan_service.py
│   ├── static/
│   │   ├── css/style.css
│   │   └── js/dashboard.js
│   └── templates/
│       ├── login.html
│       ├── base.html
│       ├── dashboard.html
│       ├── devices.html
│       ├── vulnerabilities.html
│       ├── threat_analytics.html
│       ├── network_monitoring.html
│       ├── settings.html
│       └── about.html
└── tests/
    └── test_app.py
```

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export UPOSD_ADMIN_USER=admin
export UPOSD_ADMIN_PASSWORD='change-me-strong'
export SECRET_KEY='change-me-random-secret'
python app.py
```

Open `http://127.0.0.1:5000`.

Default login is created from `UPOSD_ADMIN_USER` and `UPOSD_ADMIN_PASSWORD` on first run.
If `UPOSD_ADMIN_PASSWORD` is not set, the default password is `admin123` (change this in production).

## Core Pages

- Login Page
- Dashboard
- Device Discovery
- Vulnerability Reports
- Threat Analytics
- Network Monitoring
- Settings
- About Project

## API Endpoints

- `GET /api/dashboard/summary`
- `GET /api/devices`
- `POST /api/scans/start`
- `GET /api/scans/history`
- `GET /api/vulnerabilities`
- `GET /api/threats/alerts`
- `GET /api/network/discovery?target=192.168.1.0/24`
- `POST /api/attack-simulation`
- `GET /api/reports/download`

## Testing

```bash
python -m unittest discover -s tests -q
```

## Raspberry Pi Deployment Notes

1. Install Python 3 and pip on Raspberry Pi OS.
2. Clone the project and install dependencies.
3. Optionally install Nmap for live discovery integration:
   ```bash
   sudo apt install nmap
   ```
4. Run with Gunicorn for production:
   ```bash
   pip install gunicorn
   gunicorn -w 2 -b 0.0.0.0:5000 app:app
   ```
5. (Optional) Add reverse proxy with Nginx and systemd service for auto-start.
6. Limit network exposure in production (firewall/VPN/reverse proxy), since binding to `0.0.0.0` makes the service reachable on all interfaces.

## Security and Ethics

UPOSD is for controlled, ethical, academic simulation. Attack features are intentionally non-destructive and run in demo-safe mode.
