import random
import subprocess
from datetime import datetime

from . import db
from .models import Device, ScanLog, Vulnerability


DEMO_VULNS = [
    ("Outdated SSH version", "medium", "SSH service is running a legacy version."),
    ("Weak TLS cipher", "high", "TLS endpoint accepts deprecated ciphers."),
    ("Open admin panel", "critical", "Web admin panel exposed without IP restrictions."),
]


def seed_demo_data():
    if Device.query.count() == 0:
        devices = [
            Device(ip_address="192.168.1.10", hostname="finance-pc", open_ports="22,443"),
            Device(ip_address="192.168.1.22", hostname="iot-sensor-gw", open_ports="1883,8080"),
            Device(ip_address="192.168.1.45", hostname="lab-server", open_ports="21,22,80,3306"),
        ]
        db.session.add_all(devices)

    if Vulnerability.query.count() == 0:
        db.session.add_all(
            [
                Vulnerability(title=t, severity=s, description=d)
                for (t, s, d) in DEMO_VULNS
            ]
        )

    if ScanLog.query.count() == 0:
        db.session.add(
            ScanLog(
                target="192.168.1.0/24",
                status="completed",
                threat_level="medium",
                details="Initial baseline scan completed in demo mode.",
            )
        )

    db.session.commit()


def run_demo_scan(target):
    ports = [22, 80, 443, 3306, 8080]
    random.shuffle(ports)
    discovered_ports = sorted(ports[: random.randint(2, 4)])
    threat_level = random.choice(["low", "medium", "high"])

    details = f"Scanned {target}. Open ports: {','.join(str(p) for p in discovered_ports)}"

    log = ScanLog(
        target=target,
        status="completed",
        threat_level=threat_level,
        details=details,
    )
    db.session.add(log)
    db.session.commit()

    return {
        "target": target,
        "threat_level": threat_level,
        "open_ports": discovered_ports,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "mode": "safe-demo",
    }


def run_nmap_discovery(target):
    try:
        output = subprocess.check_output(["nmap", "-sn", target], text=True, timeout=30)
        return {"mode": "nmap", "output": output}
    except Exception:
        return {"mode": "safe-demo", "output": "Nmap unavailable. Demo discovery enabled."}
