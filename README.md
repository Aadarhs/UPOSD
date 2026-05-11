# UPOSD - Universal Portable Offensive Security Device

UPOSD is a full-stack academic cybersecurity platform that simulates a portable offensive security and enterprise monitoring device (Raspberry Pi oriented) with a modern web dashboard.

## Features

- Flask + SQLite modular backend
- Flask-Login authentication (`admin` / `admin123` demo credentials)
- REST API architecture for dashboards and scan workflows
- Safe-mode network scan simulation (Nmap-inspired)
- Vulnerability tracking and reporting
- Device discovery and IoT monitoring panel
- Threat analytics with Chart.js visualizations
- Network monitoring and packet activity simulation
- Live terminal-style activity feed
- Responsive dark glassmorphism cybersecurity UI

## Project Structure

```
UPOSD/
├── app/
│   ├── blueprints/
│   │   ├── api/routes.py
│   │   ├── auth/routes.py
│   │   └── main/routes.py
│   ├── static/
│   │   ├── css/style.css
│   │   └── js/dashboard.js
│   ├── templates/
│   │   ├── about.html
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── device_discovery.html
│   │   ├── login.html
│   │   ├── network_monitoring.html
│   │   ├── settings.html
│   │   ├── threat_analytics.html
│   │   └── vulnerability_reports.html
│   ├── __init__.py
│   ├── config.py
│   ├── extensions.py
│   ├── models.py
│   └── sample_data.py
├── instance/
├── requirements.txt
└── run.py
```

## Installation

1. Clone and open the repository.
2. Create and activate a virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the app:

```bash
python run.py
```

5. Open `http://127.0.0.1:5000`.

## REST API Highlights

- `GET /api/dashboard/summary`
- `GET /api/devices`
- `POST /api/scans/start`
- `GET /api/scans/history`
- `GET /api/vulnerabilities`
- `GET /api/alerts`
- `GET /api/activity-feed`
- `GET /api/network/topology`
- `GET /api/packets/live`
- `GET /api/reports/vulnerabilities`

## Raspberry Pi Deployment (Lightweight)

1. Install Python 3.11+ and `pip`.
2. Copy project to Raspberry Pi.
3. Install dependencies via `pip install -r requirements.txt`.
4. Run using `python run.py` for demo, or serve with Gunicorn:

```bash
pip install gunicorn
gunicorn -w 2 -b 0.0.0.0:5000 run:app
```

5. (Optional) configure as a `systemd` service for auto-start.

## Notes

- This project intentionally uses **safe/demo attack simulation mode only**.
- No real exploitation payloads are included.
- Designed for university final-year presentation and demonstration.
