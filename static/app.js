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

function downloadCSV() {
  const rows = window.lastResults;
  if (!rows || rows.length === 0) return;

  let csv = [
    Object.keys(rows[0]).join(","),
    ...rows.map(r => Object.values(r).map(x => `"${String(x).replace(/"/g, '""')}"`).join(","))
  ].join("\n");

  const blob = new Blob([csv], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "leads.csv";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}
