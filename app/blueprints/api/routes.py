from datetime import datetime
import ipaddress
from random import choice, randint

from flask import Blueprint, jsonify, request
from flask_login import login_required

from ...extensions import db
from ...models import ActivityLog, Alert, Device, Scan, Vulnerability

api_bp = Blueprint("api", __name__)


def model_to_dict(model, fields):
    return {field: getattr(model, field) for field in fields}


@api_bp.get("/dashboard/summary")
@login_required
def dashboard_summary():
    total_devices = Device.query.count()
    online_devices = Device.query.filter_by(status="online").count()
    vuln_count = Vulnerability.query.filter_by(status="open").count()
    high_alerts = Alert.query.filter(Alert.level.in_(["high", "critical"])).count()
    scans_today = Scan.query.count()

    threat_score = min(100, (vuln_count * 8) + (high_alerts * 12))
    threat_level = (
        "critical"
        if threat_score >= 80
        else "high"
        if threat_score >= 55
        else "medium"
        if threat_score >= 30
        else "low"
    )

    return jsonify(
        {
            "devices": {
                "total": total_devices,
                "online": online_devices,
                "offline": max(total_devices - online_devices, 0),
            },
            "vulnerabilities": vuln_count,
            "high_alerts": high_alerts,
            "scans_today": scans_today,
            "threat_score": threat_score,
            "threat_level": threat_level,
        }
    )


@api_bp.get("/devices")
@login_required
def list_devices():
    devices = Device.query.order_by(Device.last_seen.desc()).all()
    payload = [
        {
            **model_to_dict(
                device,
                [
                    "id",
                    "hostname",
                    "ip_address",
                    "mac_address",
                    "status",
                    "threat_level",
                    "device_type",
                ],
            ),
            "last_seen": device.last_seen.isoformat(),
        }
        for device in devices
    ]
    return jsonify(payload)


@api_bp.post("/scans/start")
@login_required
def start_scan():
    data = request.get_json(silent=True) or {}
    target = (data.get("target") or "192.168.10.0/24").strip()[:255]
    mode = (data.get("mode") or "safe-demo").strip()[:50]

    try:
        if "/" in target:
            ipaddress.ip_network(target, strict=False)
        else:
            ipaddress.ip_address(target)
    except ValueError:
        return jsonify({"message": "Invalid scan target. Use a valid IP or CIDR notation."}), 400

    open_ports = randint(1, 15)
    vulnerabilities = randint(0, 6)
    output = (
        f"[SCAN] Mode={mode} Target={target}\n"
        "[SCAN] Discovering live hosts...\n"
        f"[SCAN] Open ports identified: {open_ports}\n"
        f"[SCAN] Potential vulnerabilities: {vulnerabilities}\n"
        "[DONE] Safe simulation complete."
    )

    scan = Scan(
        target=target,
        scan_type="nmap-safe-simulated",
        status="completed",
        open_ports=open_ports,
        vulnerabilities_found=vulnerabilities,
        output_log=output,
    )
    db.session.add(scan)
    db.session.add(ActivityLog(event=f"[SCAN] Safe simulated scan executed against {target}"))
    db.session.commit()

    return jsonify({"message": "Simulated scan completed.", "scan_id": scan.id, "output": output})


@api_bp.get("/scans/history")
@login_required
def scan_history():
    scans = Scan.query.order_by(Scan.created_at.desc()).limit(50).all()
    return jsonify(
        [
            {
                "id": scan.id,
                "target": scan.target,
                "scan_type": scan.scan_type,
                "status": scan.status,
                "open_ports": scan.open_ports,
                "vulnerabilities_found": scan.vulnerabilities_found,
                "output_log": scan.output_log,
                "created_at": scan.created_at.isoformat(),
            }
            for scan in scans
        ]
    )


@api_bp.get("/vulnerabilities")
@login_required
def vulnerabilities():
    vulns = Vulnerability.query.order_by(Vulnerability.created_at.desc()).all()
    return jsonify(
        [
            {
                "id": vuln.id,
                "cve_id": vuln.cve_id,
                "title": vuln.title,
                "severity": vuln.severity,
                "asset": vuln.asset,
                "status": vuln.status,
                "recommendation": vuln.recommendation,
                "created_at": vuln.created_at.isoformat(),
            }
            for vuln in vulns
        ]
    )


@api_bp.get("/alerts")
@login_required
def alerts():
    alerts = Alert.query.order_by(Alert.created_at.desc()).limit(30).all()
    return jsonify(
        [
            {
                "id": alert.id,
                "title": alert.title,
                "level": alert.level,
                "source": alert.source,
                "details": alert.details,
                "created_at": alert.created_at.isoformat(),
            }
            for alert in alerts
        ]
    )


@api_bp.get("/activity-feed")
@login_required
def activity_feed():
    rows = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(25).all()
    return jsonify(
        [
            {
                "id": row.id,
                "event": row.event,
                "level": row.level,
                "created_at": row.created_at.isoformat(),
            }
            for row in rows
        ]
    )


@api_bp.get("/threat/series")
@login_required
def threat_series():
    labels = [f"T-{i}" for i in range(12)]
    data = [randint(15, 95) for _ in range(12)]
    return jsonify({"labels": labels, "data": data})


@api_bp.get("/network/topology")
@login_required
def network_topology():
    nodes = [
        {"id": "gateway", "group": "core"},
        {"id": "uposd-pi", "group": "security"},
    ]
    links = [{"source": "uposd-pi", "target": "gateway"}]

    for device in Device.query.limit(10).all():
        node_id = f"{device.hostname}-{device.id}"
        nodes.append({"id": node_id, "group": device.device_type.lower()})
        links.append({"source": "gateway", "target": node_id})

    return jsonify({"nodes": nodes, "links": links})


@api_bp.get("/packets/live")
@login_required
def packet_stream():
    protocols = ["TCP", "UDP", "HTTP", "TLS", "MQTT", "ICMP"]
    rows = [
        {
            "timestamp": datetime.utcnow().isoformat(),
            "source": f"192.168.10.{randint(10, 250)}",
            "destination": f"10.0.0.{randint(2, 250)}",
            "protocol": choice(protocols),
            "bytes": randint(64, 2048),
            "anomaly": choice([False, False, False, True]),
        }
        for _ in range(10)
    ]
    return jsonify(rows)


@api_bp.get("/reports/vulnerabilities")
@login_required
def vulnerability_report():
    vulns = Vulnerability.query.order_by(Vulnerability.severity.desc()).all()
    lines = ["UPOSD Vulnerability Report", "=" * 30]
    for item in vulns:
        lines.extend(
            [
                f"{item.cve_id} | {item.severity.upper()} | {item.asset}",
                f"Title: {item.title}",
                f"Recommendation: {item.recommendation}",
                "-" * 30,
            ]
        )

    return jsonify({"generated": datetime.utcnow().isoformat(), "content": "\n".join(lines)})
