const apiGet = async (path) => {
  const response = await fetch(path);
  if (!response.ok) throw new Error(`Failed request (${response.status} ${response.statusText}): ${path}`);
  return response.json();
};

const updateDashboard = async () => {
  const el = (id) => document.getElementById(id);
  const summaryRoot = el("kpi-devices");
  if (!summaryRoot) return;

  const summary = await apiGet("/api/dashboard/summary");
  el("kpi-devices").textContent = summary.devices.total;
  el("kpi-online").textContent = summary.devices.online;
  el("kpi-vulns").textContent = summary.vulnerabilities;
  el("kpi-threat").textContent = `${summary.threat_score} (${summary.threat_level.toUpperCase()})`;

  const series = await apiGet("/api/threat/series");
  const canvas = document.getElementById("threatChart");
  if (canvas) {
    if (window.uposdThreatChart) window.uposdThreatChart.destroy();
    window.uposdThreatChart = new Chart(canvas, {
      type: "line",
      data: {
        labels: series.labels,
        datasets: [{
          label: "Threat Index",
          data: series.data,
          borderColor: "#0ff5d4",
          backgroundColor: "rgba(15,245,212,.12)",
          tension: 0.35,
          fill: true,
        }],
      },
      options: { plugins: { legend: { display: false } } },
    });
  }

  const feed = await apiGet("/api/activity-feed");
  const feedEl = document.getElementById("activityFeed");
  if (feedEl) {
    feedEl.innerHTML = feed.map((item) => `[${new Date(item.created_at).toLocaleTimeString()}] ${item.event}`).join("<br>");
  }
};

const bindScanForm = () => {
  const form = document.getElementById("scanForm");
  if (!form) return;
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const target = document.getElementById("scanTarget").value || "192.168.10.0/24";
    const mode = document.getElementById("scanMode").value;
    const response = await fetch("/api/scans/start", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ target, mode }),
    });
    const data = await response.json();
    document.getElementById("scanOutput").textContent = data.output || data.message;
    await updateDashboard();
  });
};

const loadDevices = async () => {
  const table = document.getElementById("deviceTableBody");
  if (!table) return;
  const devices = await apiGet("/api/devices");
  table.innerHTML = devices.map((d) => `
    <tr>
      <td>${d.hostname}</td><td>${d.ip_address}</td><td>${d.mac_address || "-"}</td>
      <td>${d.device_type}</td><td>${d.status}</td><td>${d.threat_level}</td>
      <td>${new Date(d.last_seen).toLocaleString()}</td>
    </tr>`).join("");
};

const loadVulnerabilities = async () => {
  const table = document.getElementById("vulnTableBody");
  if (!table) return;
  const vulns = await apiGet("/api/vulnerabilities");
  table.innerHTML = vulns.map((v) => `
    <tr><td>${v.cve_id}</td><td>${v.title}</td><td>${v.severity}</td><td>${v.asset}</td><td>${v.status}</td></tr>
  `).join("");

  const reportBtn = document.getElementById("downloadReportBtn");
  const reportOutput = document.getElementById("reportOutput");
  if (reportBtn && reportOutput) {
    reportBtn.addEventListener("click", async () => {
      const report = await apiGet("/api/reports/vulnerabilities");
      reportOutput.textContent = report.content;
    });
  }
};

const loadAlerts = async () => {
  const list = document.getElementById("alertsList");
  const canvas = document.getElementById("threatDonut");
  if (!list && !canvas) return;

  const alerts = await apiGet("/api/alerts");
  if (list) {
    list.innerHTML = alerts.map((a) => `<li class="alert-item ${a.level}"><strong>${a.level.toUpperCase()}</strong> - ${a.title}<br><small>${a.details}</small></li>`).join("");
  }

  if (canvas) {
    const buckets = { low: 0, medium: 0, high: 0, critical: 0 };
    alerts.forEach((a) => { buckets[a.level] = (buckets[a.level] || 0) + 1; });
    if (window.uposdDonutChart) window.uposdDonutChart.destroy();
    window.uposdDonutChart = new Chart(canvas, {
      type: "doughnut",
      data: {
        labels: Object.keys(buckets),
        datasets: [{
          data: Object.values(buckets),
          backgroundColor: ["#0ff5d4", "#4c7dff", "#ffa502", "#ff4757"],
        }],
      },
    });
  }
};

const loadPacketTable = async () => {
  const table = document.getElementById("packetTableBody");
  const topology = document.getElementById("topologyOutput");
  if (!table && !topology) return;

  if (table) {
    const packets = await apiGet("/api/packets/live");
    table.innerHTML = packets.map((p) => `
      <tr>
        <td>${new Date(p.timestamp).toLocaleTimeString()}</td>
        <td>${p.source}</td>
        <td>${p.destination}</td>
        <td>${p.protocol}</td>
        <td>${p.bytes}</td>
        <td>${p.anomaly ? "⚠️" : "-"}</td>
      </tr>`).join("");
  }

  if (topology) {
    const map = await apiGet("/api/network/topology");
    topology.textContent = JSON.stringify(map, null, 2);
  }
};

const bootstrap = async () => {
  try {
    const pageLoaders = [];
    if (document.getElementById("kpi-devices")) pageLoaders.push(updateDashboard());
    if (document.getElementById("deviceTableBody")) pageLoaders.push(loadDevices());
    if (document.getElementById("vulnTableBody")) pageLoaders.push(loadVulnerabilities());
    if (document.getElementById("alertsList") || document.getElementById("threatDonut")) pageLoaders.push(loadAlerts());
    if (document.getElementById("packetTableBody") || document.getElementById("topologyOutput")) pageLoaders.push(loadPacketTable());
    await Promise.all(pageLoaders);
    bindScanForm();
    const hasDashboard = Boolean(document.getElementById("kpi-devices"));
    const hasNetwork = Boolean(document.getElementById("packetTableBody") || document.getElementById("topologyOutput"));
    setInterval(() => {
      if (hasDashboard) updateDashboard().catch(() => {});
      if (hasNetwork) loadPacketTable().catch(() => {});
    }, 8000);
  } catch (error) {
    console.error(error);
  }
};

document.addEventListener("DOMContentLoaded", bootstrap);
