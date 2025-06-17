document.getElementById("lead-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const input = document.getElementById("input").value;

  const response = await fetch("http://localhost:8000/generate-email/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ input })
  });

  const data = await response.json();
  document.getElementById("result").innerText = data.email || "Error generating email.";
});
