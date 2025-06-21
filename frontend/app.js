// app.js

function switchTab(tabId) {
  document.querySelectorAll('.tab-content').forEach(tab => tab.style.display = 'none');
  document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));

  document.getElementById(tabId).style.display = 'block';
  const activeBtn = Array.from(document.getElementsByClassName('tab-button')).find(btn => btn.innerText.toLowerCase().includes(tabId));
  if (activeBtn) activeBtn.classList.add('active');
}

async function submitMapsSearch() {
  const query = document.getElementById("mapsInput").value.trim();
  const status = document.getElementById("status");
  const resultArea = document.getElementById("resultArea");
  const downloadBtn = document.getElementById("downloadBtn");

  if (!query) return alert("Please enter a search term.");

  status.innerText = "Scraping Google Maps...";
  resultArea.innerHTML = "";
  downloadBtn.style.display = "none";

  try {
    const response = await fetch("http://localhost:8000/scrape-lead/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ input: query }),
    });

    const data = await response.json();

    if (!Array.isArray(data) || data.length === 0) {
      status.innerText = "No results found.";
      return;
    }

    status.innerText = `✅ Found ${data.length} leads!`;

    let table = "<table><tr><th>Name</th><th>Phone</th><th>Website</th><th>Email</th><th>Link</th></tr>";
    data.forEach(item => {
      table += `<tr>
        <td>${item.Name}</td>
        <td>${item.Phone}</td>
        <td><a href="${item.Website}" target="_blank">${item.Website}</a></td>
        <td>${item.Email || ""}</td>
        <td><a href="${item.Link}" target="_blank">Map</a></td>
      </tr>`;
    });

    table += "</table>";

    resultArea.innerHTML = table;
    window.lastResults = data;
    downloadBtn.style.display = "inline-block";
  } catch (err) {
    status.innerText = "❌ Error: " + err.message;
  }
}

async function submitWebsiteScrape() {
  const url = document.getElementById("websiteInput").value.trim();
  const status = document.getElementById("status");
  const resultArea = document.getElementById("resultArea");
  const downloadBtn = document.getElementById("downloadBtn");

  if (!url) return alert("Please enter a website URL.");

  status.innerText = "Scraping website...";
  resultArea.innerHTML = "";
  downloadBtn.style.display = "none";

  try {
    const response = await fetch("http://localhost:8001/scrape-website/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ input: url }),
    });

    const data = await response.json();
    console.log("✅ Website scrape response:", data);

    if (!Array.isArray(data) || data.length === 0) {
      status.innerText = "❌ No contact info found.";
      return;
    }

    // Build HTML table
    let html = "<table><tr><th>Name</th><th>Phone</th><th>Email</th></tr>";
    data.forEach(entry => {
    html += `<tr>
    <td>${entry.Name || ""}</td>
    <td>${entry.Phone || ""}</td>
    <td>${entry.Email || ""}</td>
  </tr>`;
});

    html += "</table>";

    resultArea.innerHTML = html;
    window.lastResults = data;
    downloadBtn.style.display = "inline-block";
    status.innerText = `✅ Found ${data.length} contact entries.`;
  } catch (err) {
    status.innerText = "❌ Error: " + err.message;
  }
}


function downloadCSV() {
  const rows = window.lastResults;
  if (!rows || rows.length === 0) return;

  let csv = "";

  if (Array.isArray(rows)) {
    csv = [
      Object.keys(rows[0]).join(","),
      ...rows.map(r => Object.values(r).map(x => `"${String(x).replace(/"/g, '""')}"`).join(","))
    ].join("\n");
  } else {
    const keys = Object.keys(rows).filter(k => Array.isArray(rows[k]));
    csv = "Type,Value\n";
    keys.forEach(key => {
      rows[key].forEach(value => {
        csv += `${key},"${value}"\n`;
      });
    });
  }

  const blob = new Blob([csv], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "leads.csv";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}
