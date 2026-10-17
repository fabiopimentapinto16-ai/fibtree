let map, radarLayers = [], rotaLayer = null, modoAmostra = false, modoDetector = false;
map = L.map('map').setView([-15, -50], 4);
L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', { maxZoom: 19 }).addTo(map);

map.on('click', function(e) {
    let lat = e.latlng.lat.toFixed(6), lng = e.latlng.lng.toFixed(6);
    document.getElementById('lat').value = lat; document.getElementById('lng').value = lng;
    if (modoAmostra) { L.marker([lat, lng]).addTo(map).bindPopup('Amostra').openPopup(); modoAmostra = false; return; }
    if (modoDetector) { L.circle([lat, lng], { radius: 500, color: '#00ff88', dashArray: '5,5' }).addTo(map); alert("⛏ MODO DETECTOR ATIVADO! Procure aluviões nas margens."); modoDetector = false; return; }
    desenharRadar(lat, lng);
});

function desenharRadar(lat, lng) {
    radarLayers.forEach(l => map.removeLayer(l)); radarLayers = [];
    let raios = [5000, 4000, 3000, 2000, 1000], cores = ["#ff0000", "#ff3300", "#ff6600", "#ff9900", "#ffcc00"];
    raios.forEach((r, i) => radarLayers.push(L.circle([lat, lng], { radius: r, color: cores[i], fillOpacity: 0.2, weight: 1 }).addTo(map)));
    map.setView([lat, lng], 12);
}

async function analisar() {
    let lat = document.getElementById('lat').value, lng = document.getElementById('lng').value;
    if (!lat || !lng) return alert('Preencha as coordenadas');
    let btn = document.getElementById('btn-analisar'); btn.innerText = 'ANALISANDO...';
    try {
        let res = await fetch('/api/analisar', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({lat: parseFloat(lat), lng: parseFloat(lng)}) });
        let dados = await res.json();
        desenharRadar(lat, lng);
        document.getElementById('resultado').innerHTML = `<div class="result-box"><strong>Score: ${dados.score_final}/100</strong><br>Classificação: ${dados.classificacao}</div>`;
        let hist = JSON.parse(localStorage.getItem('historico') || '[]'); hist.push({lat, lng, score: dados.score_final, data: new Date().toISOString(), dados}); localStorage.setItem('historico', JSON.stringify(hist));
        window.ultimaAnalise = dados;
    } catch (e) { alert('Erro: ' + e.message); }
    btn.innerText = '🔍 ANALISAR POTENCIAL';
}

function abrirHistorico() { let h = JSON.parse(localStorage.getItem('historico') || '[]'); document.getElementById('listaHistorico').innerHTML = h.length ? h.map(x => `<div>Lat: ${x.lat} | Score: ${x.score}</div>`).join('') : '<p>Vazio</p>'; document.getElementById('modalHistorico').style.display = 'flex'; }
function fecharModal(id) { document.getElementById(id).style.display = 'none'; }
function exportarCSV() { let h = JSON.parse(localStorage.getItem('historico') || '[]'); if(!h.length) return; let a = document.createElement('a'); a.href = URL.createObjectURL(new Blob(['Lat,Lng,Score\n' + h.map(x => `${x.lat},${x.lng},${x.score}`).join('\n')], {type: 'text/csv'})); a.download = 'hist.csv'; a.click(); }
function ativarModoAmostra() { modoAmostra = true; alert('Clique no mapa'); }
function ativarDetectorismo() { modoDetector = true; alert('Clique no mapa'); }
function toggleRota() { if(rotaLayer) { map.removeLayer(rotaLayer); rotaLayer = null; return; } navigator.geolocation.getCurrentPosition(p => { fetch(`https://router.project-osrm.org/route/v1/driving/${p.coords.longitude},${p.coords.latitude};${document.getElementById('lng').value},${document.getElementById('lat').value}?overview=full&geometries=geojson`).then(r=>r.json()).then(d => { rotaLayer = L.polyline(d.routes[0].geometry.coordinates.map(c=>[c[1],c[0]]), {color:'yellow', weight:5}).addTo(map); map.fitBounds(rotaLayer.getBounds()); }); }); }
function gerarPDF() { if(!window.ultimaAnalise) return alert('Analise primeiro'); fetch('/api/gerar-pdf', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(window.ultimaAnalise) }).then(r=>r.blob()).then(b => { let a = document.createElement('a'); a.href = URL.createObjectURL(b); a.download = 'relatorio.pdf'; a.click(); }); }
function abrir3D() { document.getElementById('modal3D').style.display = 'flex'; let c = document.getElementById('canvas3d'); c.innerHTML=''; let s = new THREE.Scene(), cam = new THREE.PerspectiveCamera(45, c.clientWidth/c.clientHeight, 0.1, 1000); cam.position.set(8,6,10); cam.lookAt(0,0,0); let r = new THREE.WebGLRenderer({antialias:true}); r.setSize(c.clientWidth, c.clientHeight); c.appendChild(r.domElement); s.add(new THREE.AmbientLight(0xffffff, 0.6)); let l = new THREE.DirectionalLight(0xffffff, 0.8); l.position.set(10,15,10); s.add(l); [0x8B7355, 0xA0522D, 0xFFD700, 0x696969].forEach((cor, i) => { let g = new THREE.BoxGeometry(6, 0.8, 6), m = new THREE.MeshPhongMaterial({color:cor, transparent:true, opacity:0.9}), mesh = new THREE.Mesh(g, m); mesh.position.y = 1 - (i*0.8); s.add(mesh); }); function anim(){ requestAnimationFrame(anim); s.rotation.y += 0.005; r.render(s, cam); } anim(); }
