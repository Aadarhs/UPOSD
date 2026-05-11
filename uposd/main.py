import io

from flask import Blueprint, jsonify, render_template, request, send_file
from flask_login import login_required

from .models import Device, ScanLog, Vulnerability
from .scan_service import run_demo_scan, run_nmap_discovery


main_bp = Blueprint("main", __name__)
MAX_SCAN_HISTORY = 50


@main_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


@main_bp.route("/devices")
@login_required
def devices_page():
    return render_template("devices.html")


@main_bp.route("/vulnerabilities")
@login_required
def vulnerabilities_page():
    return render_template("vulnerabilities.html")


@main_bp.route("/threat-analytics")
@login_required
def threat_analytics_page():
    return render_template("threat_analytics.html")


@main_bp.route("/network-monitoring")
@login_required
def network_monitoring_page():
    return render_template("network_monitoring.html")


@main_bp.route("/settings")
@login_required
def settings_page():
    return render_template("settings.html")


@main_bp.route("/about")
@login_required
def about_page():
    return render_template("about.html")


@main_bp.route("/api/dashboard/summary")
@login_required
def dashboard_summary():
    return jsonify(
        {
            "devices": Device.query.count(),
            "vulnerabilities": Vulnerability.query.count(),
            "scans": ScanLog.query.count(),
            "threat_level": "medium",
        }
    )


@main_bp.route("/api/devices")
@login_required
def device_list():
    devices = Device.query.order_by(Device.last_seen.desc()).all()
    return jsonify(
        [
            {
                "ip_address": d.ip_address,
                "hostname": d.hostname,
                "status": d.status,
                "open_ports": d.open_ports,
                "last_seen": d.last_seen.isoformat(),
            }
            for d in devices
        ]
    )


@main_bp.route("/api/scans/start", methods=["POST"])
@login_required
def start_scan():
    payload = request.get_json(silent=True) or {}
    target = payload.get("target", "192.168.1.0/24")
    result = run_demo_scan(target)
    return jsonify(result), 201


@main_bp.route("/api/scans/history")
@login_required
def scan_history():
    logs = ScanLog.query.order_by(ScanLog.created_at.desc()).limit(MAX_SCAN_HISTORY).all()
    return jsonify(
        [
            {
                "target": log.target,
                "status": log.status,
                "threat_level": log.threat_level,
                "details": log.details,
                "created_at": log.created_at.isoformat(),
            }
            for log in logs
        ]
    )


@main_bp.route("/api/vulnerabilities")
@login_required
def vulnerability_list():
    vulns = Vulnerability.query.order_by(Vulnerability.detected_at.desc()).all()
    return jsonify(
        [
            {
                "title": v.title,
                "severity": v.severity,
                "description": v.description,
                "detected_at": v.detected_at.isoformat(),
            }
            for v in vulns
        ]
    )


@main_bp.route("/api/threats/alerts")
@login_required
def threat_alerts():
    return jsonify(
        {
            "alerts": [
                {"level": "high", "message": "Abnormal port scan frequency from 192.168.1.45"},
                {"level": "medium", "message": "IoT gateway latency spike detected"},
            ]
        }
    )


@main_bp.route("/api/network/discovery")
@login_required
def network_discovery():
    target = request.args.get("target", "192.168.1.0/24")
    return jsonify(run_nmap_discovery(target))


@main_bp.route("/api/attack-simulation", methods=["POST"])
@login_required
def attack_simulation():
    payload = request.get_json(silent=True) or {}
    scenario = payload.get("scenario", "credential-stuffing")
    return jsonify(
        {
            "mode": "safe-demo",
            "scenario": scenario,
            "result": "Simulation completed without live network exploitation.",
        }
    )


@main_bp.route("/api/reports/download")
@login_required
def download_report():
    content = "target,status,threat_level\n" + "\n".join(
        f"{log.target},{log.status},{log.threat_level}" for log in ScanLog.query.all()
    )
    return send_file(
        io.BytesIO(content.encode("utf-8")),
        as_attachment=True,
        download_name="scan_report.csv",
        mimetype="text/csv",
    )
