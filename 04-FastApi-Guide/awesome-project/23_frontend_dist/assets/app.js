document.getElementById('path').textContent = location.pathname;
fetch('/api/hello').then(r => r.json()).then(d => document.getElementById('api').textContent = JSON.stringify(d));
