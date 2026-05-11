const HISTORY_POINTS_LIMIT = 8;
const THREAT_LEVEL_SCORE = {low:1,medium:2,high:3};
const MAX_FEED_LINES = 80;
const FEED_UPDATE_INTERVAL_MS = 2200;

async function getJson(url, opts){
  const r=await fetch(url,opts);
  if(!r.ok){console.error(`Request failed: ${url} (${r.status})`);return null;}
  return r.json();
}

async function loadDashboard(){
  const summary=await getJson('/api/dashboard/summary');
  if(!summary) return;
  const byId=(id)=>document.getElementById(id);
  if(byId('kpi-devices')) byId('kpi-devices').textContent=summary.devices;
  if(byId('kpi-vulns')) byId('kpi-vulns').textContent=summary.vulnerabilities;
  if(byId('kpi-scans')) byId('kpi-scans').textContent=summary.scans;
  if(byId('kpi-threat')) byId('kpi-threat').textContent=summary.threat_level.toUpperCase();

  const history=await getJson('/api/scans/history')||[];
  const labels=history.slice(0,HISTORY_POINTS_LIMIT).map((_,i)=>`Scan ${i+1}`);
  const points=history.slice(0,HISTORY_POINTS_LIMIT).map(l=>THREAT_LEVEL_SCORE[l.threat_level]||1);

  ['threatChart','threatChartFull'].forEach((id)=>{
    const c=document.getElementById(id);
    if(!c) return;
    new Chart(c,{type:'line',data:{labels,datasets:[{label:'Threat trend',data:points,borderColor:'#00ffc6',tension:.35}]},options:{plugins:{legend:{labels:{color:'#d9f9ff'}}},scales:{x:{ticks:{color:'#d9f9ff'}},y:{ticks:{color:'#d9f9ff'}}}}});
  });

  const feed=document.getElementById('feed');
  if(feed){
    const lines=['[OK] Sensor link established','[INFO] Monitoring packet stream','[WARN] Suspicious behavior score at 67/100'];
    let i=0;setInterval(()=>{const next=`${feed.textContent}\n${lines[i%lines.length]}`.split('\n').slice(-MAX_FEED_LINES).join('\n');feed.textContent=next;i++;},FEED_UPDATE_INTERVAL_MS);
  }
}

async function loadDevices(){
  const rows=(await getJson('/api/devices'))||[];
  const tbody=document.querySelector('#devices-table tbody');
  if(!tbody) return;
  tbody.innerHTML=rows.map(r=>`<tr><td>${r.ip_address}</td><td>${r.hostname}</td><td>${r.status}</td><td>${r.open_ports}</td></tr>`).join('');
}

async function loadVulns(){
  const vulns=(await getJson('/api/vulnerabilities'))||[];
  const list=document.getElementById('vuln-list');
  if(list){list.innerHTML=vulns.map(v=>`<li><b>${v.severity.toUpperCase()}</b> - ${v.title}: ${v.description}</li>`).join('');}
  const dl=document.getElementById('download-report');
  if(dl){dl.onclick=()=>{window.location='/api/reports/download';};}
}

function wireScan(){
  const btn=document.getElementById('run-scan');
  const out=document.getElementById('scan-output');
  const target=document.getElementById('scan-target');
  if(!btn||!out) return;
  btn.onclick=async ()=>{
    const scanTarget=(target?.value||'192.168.1.0/24').trim();
    const result=await getJson('/api/scans/start',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({target:scanTarget})});
    if(result){out.textContent=JSON.stringify(result,null,2);}
  };
}

document.addEventListener('DOMContentLoaded',()=>{loadDashboard();loadDevices();loadVulns();wireScan();});
