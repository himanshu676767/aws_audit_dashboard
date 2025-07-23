function runAudit(type) {
  fetch(`/api/audit/${type}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ profile: "default", region: "us-east-1", dry_run: false })
  })
  .then(res => res.json())
  .then(data => {
    document.getElementById('results').textContent = JSON.stringify(data, null, 2);
  });
}


function runAudit(type) {
  const profile = document.getElementById('profile').value;
  const region = document.getElementById('region').value;

  fetch(`/api/audit/${type}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ profile, region, dry_run: false })
  })
  .then(res => res.json())
  .then(data => {
    document.getElementById('results').textContent = JSON.stringify(data, null, 2);
  });
}