import os
import secrets
from pathlib import Path
from random import choice, randint

from flask import current_app

from .extensions import db
from .models import ActivityLog, Alert, Device, Scan, User, Vulnerability


THREAT_LEVELS = ["low", "medium", "high", "critical"]


def ensure_seed_data():
    if not User.query.filter_by(username="admin").first():
        admin = User(username="admin", role="administrator")
        admin_password = os.environ.get("UPOSD_ADMIN_PASSWORD")
        if not admin_password:
            if os.environ.get("FLASK_ENV") == "production":
                raise RuntimeError(
                    "UPOSD_ADMIN_PASSWORD must be set when FLASK_ENV=production."
                )
            admin_password = secrets.token_urlsafe(16)
            password_file = Path(current_app.instance_path) / "initial_admin_password.txt"
            if not password_file.exists():
                password_file.write_text(f"{admin_password}\n", encoding="utf-8")
        admin.set_password(admin_password)
        db.session.add(admin)

    if Device.query.count() == 0:
        for i in range(1, 8):
            db.session.add(
                Device(
                    hostname=f"iot-node-{i}",
                    ip_address=f"192.168.10.{100 + i}",
                    mac_address=f"B8:27:EB:AA:10:{i:02}",
                    status=choice(["online", "online", "offline"]),
                    threat_level=choice(THREAT_LEVELS),
                    device_type=choice(["IoT", "Workstation", "Server", "Router"]),
                )
            )

    if Vulnerability.query.count() == 0:
        db.session.add_all(
            [
                Vulnerability(
                    cve_id="CVE-2023-12345",
                    title="Outdated TLS configuration",
                    severity="high",
                    asset="edge-router-1",
                    recommendation="Disable legacy ciphers and enforce TLS 1.2+.",
                ),
                Vulnerability(
                    cve_id="CVE-2022-99887",
                    title="Default credentials detected",
                    severity="critical",
                    asset="iot-node-3",
                    recommendation="Rotate credentials and enforce MFA where applicable.",
                ),
                Vulnerability(
                    cve_id="CVE-2024-45678",
                    title="Weak SSH key exchange",
                    severity="medium",
                    asset="linux-host-5",
                    recommendation="Enable curve25519-sha256 and disable weak KEX algorithms.",
                ),
            ]
        )

    if Scan.query.count() == 0:
        for i in range(5):
            target = f"192.168.10.{10 + i}"
            open_ports = randint(2, 10)
            vulns = randint(0, 5)
            log = (
                f"[NMAP] Host {target} is up.\n"
                f"[NMAP] {open_ports} open ports discovered.\n"
                f"[VULN] {vulns} potential vulnerabilities detected.\n"
                "[DONE] Simulated scan complete."
            )
            db.session.add(
                Scan(
                    target=target,
                    open_ports=open_ports,
                    vulnerabilities_found=vulns,
                    output_log=log,
                )
            )

    if Alert.query.count() == 0:
        db.session.add_all(
            [
                Alert(
                    title="Suspicious SMB traffic",
                    level="high",
                    source="packet-monitor",
                    details="Lateral movement pattern detected from 192.168.10.121",
                ),
                Alert(
                    title="Brute-force login simulation",
                    level="medium",
                    source="attack-simulator",
                    details="Safe-mode credential spray simulation triggered.",
                ),
            ]
        )

    if ActivityLog.query.count() == 0:
        events = [
            "[SYS] UPOSD control plane initialized",
            "[SCAN] Demo Nmap scan completed",
            "[IOT] iot-node-4 heartbeat restored",
            "[ALERT] Threat level moved to HIGH",
        ]
        for event in events:
            db.session.add(ActivityLog(event=event))

    db.session.commit()
