from flask import Blueprint, render_template
from flask_login import login_required

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def root():
    return render_template("about.html")


@main_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", page_title="Dashboard")


@main_bp.route("/devices")
@login_required
def devices():
    return render_template("device_discovery.html", page_title="Device Discovery")


@main_bp.route("/vulnerabilities")
@login_required
def vulnerabilities():
    return render_template("vulnerability_reports.html", page_title="Vulnerability Reports")


@main_bp.route("/analytics")
@login_required
def analytics():
    return render_template("threat_analytics.html", page_title="Threat Analytics")


@main_bp.route("/network")
@login_required
def network():
    return render_template("network_monitoring.html", page_title="Network Monitoring")


@main_bp.route("/settings")
@login_required
def settings():
    return render_template("settings.html", page_title="Settings")


@main_bp.route("/about")
def about():
    return render_template("about.html")
