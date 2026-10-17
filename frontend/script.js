let map, radarLayers = [], rotaLayer = null, modoAmostra = false;
let ultimaAnalise = null;

// Inicializa o mapa com Aceleração de Hardware (Canvas)
map = L.map('map', {preferCanvas: true}).setView([-15, -50], 4);
L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', { maxZoom: 19 }).addTo(map);

// Controles de Escala e Tela Cheia
L.control.scale({imperial: false}).addTo(map);
L.control.fullscreen({ position: 'topleft' }).addTo(map);

// Clique no mapa
map.on('click', function(e) {
    let lat = e.latlng.lat.toFixed(6), lng = e.latlng.lng.toFixed(6);
    document.getElementById('lat').value = lat; document.getElementById('lng').value = lng;
    if (modoAmostra) { 
        L.marker([lat, lng]).addTo(map).bindPopup('Amostra Salva').openPopup(); 
        modoAmostra = false; return; 
    }
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
        let res = await fetch('/api/analisar', { 
            method: 'POST', 
            headers: {'Content-Type': 'application/json'}, 
            body: JSON.stringify({lat: parseFloat(lat), lng: parseFloat(lng)}) 
        });
        let dados = await res.json();
        
        desenharRadar(lat, lng);
        desenharPontosAnalise(dados);
        
        document.getElementById('resultado').innerHTML = `<div class="result-box">
            <strong>Score: ${dados.score_final}/100</strong><br>
            Classificação: ${dados.classificacao}<br>
            Tipo: ${dados.tipo_principal.toUpperCase()}
        </div>`;
        
        let hist = JSON.parse(localStorage.getItem('historico') || '[]'); 
        hist.push({lat, lng, score: dados.score_final, data: new Date().toISOString(), dados}); 
        localStorage.setItem('historico', JSON.stringify(hist));
        
        ultimaAnalise = dados;
    } catch (e) { alert('Erro: ' + e.message); }
    btn.innerText = '🔍 ANALISAR POTENCIAL';
}

function desenharPontosAnalise(dados) {
    // 1. Desenha os pontos do SIGMINE com Cluster
    if (dados.pontos_sigmine) {
        if (window.sigmineCluster) map.removeLayer(window.sigmineCluster);
        window.sigmineCluster = L.markerClusterGroup();
        dados.pontos_sigmine.forEach(p => {
            let popupHTML = '<b>Processo:</b> ' + p.processo + '<br>' +
                            '<b>Mineral:</b> ' + (p.subs || 'N/I') + '<br>' +
                            '<b>Fase:</b> ' + (p.fase || 'N/I') + '<br>' +
                            '<button onclick="criarRota(' + p.lat + ', ' + p.lng + ')" style="margin-top:8px; padding:8px 12px; background:#ff6400; color:#fff; border:none; border-radius:4px; font-weight:bold; cursor:pointer; width:100%;">🛣️ CRIAR ROTA</button>';
            let marker = L.circleMarker([p.lat, p.lng], {color: '#00ff88', radius: 5, fillOpacity: 0.9, weight: 2}).bindPopup(popupHTML);
            window.sigmineCluster.addLayer(marker);
        });
        map.addLayer(window.sigmineCluster);
    }

    // 2. Desenha o Ponto de Detectorismo/Interesse com Rota
    if (dados.ponto_interesse) {
        const pi = dados.ponto_interesse;
        const isOuro = dados.tipo_principal === 'ouro';
        const corPonto = isOuro ? '#FFD700' : '#00FFFF';
        const titulo = isOuro ? '⛏️ PONTO DE DETECTORISMO (OURO FLUVIAL/ALUVIONAR)' : '🎯 PONTO DE INTERESSE (TERRAS RARAS)';
        
        let popupHTML = '<b style="color:' + corPonto + ';">' + titulo + '</b><br>' +
                        '<b>Score:</b> ' + pi.score + '%<br>' +
                        '<b>Motivo:</b> ' + (pi.motivo || 'Alta probabilidade') + '<br>' +
                        '<button onclick="criarRota(' + pi.lat + ', ' + pi.lng + ')" style="margin-top:8px; padding:10px; background:#ff6400; color:#fff; border:none; border-radius:4px; font-weight:bold; cursor:pointer; width:100%;">🛣️ CRIAR ROTA PARA DETECTORISMO</button>';
        
        L.circleMarker([pi.lat, pi.lng], {color: corPonto, radius: 10, fillOpacity: 1, weight: 3})
         .addTo(map).bindPopup(popupHTML).openPopup();
    }
}

function criarRota(destLat, destLng) {
    if (!navigator.geolocation) { alert('GPS não suportado.'); return; }
    navigator.geolocation.getCurrentPosition(function(pos) {
        const url = 'https://www.google.com/maps/dir/?api=1&origin=' + pos.coords.latitude + ',' + pos.coords.longitude + '&destination=' + destLat + ',' + destLng + '&travelmode=driving';
        window.open(url, '_blank');
    }, function(err) { alert('Erro no GPS: ' + err.message); }, { enableHighAccuracy: true, timeout: 15000 });
}

function toggleRota() {
    if (rotaLayer) { map.removeLayer(rotaLayer); rotaLayer = null; return; }
    if (!ultimaAnalise) return alert('Faça uma análise primeiro');
    navigator.geolocation.getCurrentPosition(pos => {
        const url = `https://router.project-osrm.org/route/v1/driving/${pos.coords.longitude},${pos.coords.latitude};${ultimaAnalise.coordenada.lng},${ultimaAnalise.coordenada.lat}?overview=full&geometries=geojson`;
        fetch(url).then(r=>r.json()).then(d => {
            if (d.code !== 'Ok') return alert('Erro na rota');
            rotaLayer = L.polyline(d.routes[0].geometry.coordinates.map(c=>[c[1],c[0]]), {color:'yellow', weight:5}).addTo(map);
            map.fitBounds(rotaLayer.getBounds());
        });
    });
}

function ativarDetectorismo() {
    if (!ultimaAnalise) return alert('Faça uma análise primeiro para o detectorismo encontrar o ponto ideal.');
    const pi = ultimaAnalise.ponto_interesse;
    if (pi) {
        alert('⛏️ Ponto de Detectorismo encontrado! Traçando rota...');
        criarRota(pi.lat, pi.lng);
    } else {
        alert('Nenhum ponto de detectorismo ideal encontrado nesta análise.');
    }
}

// ==========================================
// FUNÇÕES DE PDF, KML E HISTÓRICO
// ==========================================
function gerarPDF() { if(!ultimaAnalise) return alert('Analise primeiro'); fetch('/api/gerar-pdf', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(ultimaAnalise) }).then(r=>r.blob()).then(b => { let a = document.createElement('a'); a.href = URL.createObjectURL(b); a.download = 'relatorio.pdf'; a.click(); }); }
function gerarMemorial() { if(!ultimaAnalise) return alert('Analise primeiro'); fetch('/api/gerar-memorial', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(ultimaAnalise) }).then(r=>r.blob()).then(b => { let a = document.createElement('a'); a.href = URL.createObjectURL(b); a.download = 'memorial.pdf'; a.click(); }); }
function exportarKML() { if(!ultimaAnalise) return alert('Analise primeiro'); fetch('/api/exportar-kml', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(ultimaAnalise) }).then(r=>r.blob()).then(b => { let a = document.createElement('a'); a.href = URL.createObjectURL(b); a.download = 'mapa.kml'; a.click(); }); }
function abrirHistorico() { let h = JSON.parse(localStorage.getItem('historico') || '[]'); document.getElementById('listaHistorico').innerHTML = h.length ? h.map(x => '<div style="border-bottom:1px solid #333; padding:10px;">Lat: ' + x.lat + ' | Score: ' + x.score + '</div>').join('') : '<p>Vazio</p>'; document.getElementById('modalHistorico').style.display = 'flex'; }
function fecharModal(id) { document.getElementById(id).style.display = 'none'; }
function exportarCSV() { let h = JSON.parse(localStorage.getItem('historico') || '[]'); if(!h.length) return; let a = document.createElement('a'); a.href = URL.createObjectURL(new Blob(['Lat,Lng,Score\n' + h.map(x => x.lat + ',' + x.lng + ',' + x.score).join('\n')], {type: 'text/csv'})); a.download = 'hist.csv'; a.click(); }
function ativarModoAmostra() { modoAmostra = true; alert('Clique no mapa para marcar a amostra.'); }
function ativarGPS() { navigator.geolocation.getCurrentPosition(p => { document.getElementById('lat').value = p.coords.latitude.toFixed(6); document.getElementById('lng').value = p.coords.longitude.toFixed(6); map.setView([p.coords.latitude, p.coords.longitude], 13); }); }

// ==========================================
// SIMULAÇÃO 3D BLINDADA
// ==========================================
function abrir3D() {
    document.getElementById('modal3D').style.display = 'flex';
    setTimeout(function() {
        let container = document.getElementById('canvas3d');
        container.innerHTML = '';
        let largura = container.clientWidth || 300;
        let altura = container.clientHeight || 300;
        
        let cena = new THREE.Scene();
        cena.background = new THREE.Color(0x020408);
        let camera = new THREE.PerspectiveCamera(45, largura/altura, 0.1, 1000);
        camera.position.set(8, 6, 10); camera.lookAt(0, 0, 0);
        let renderer = new THREE.WebGLRenderer({antialias: true});
        renderer.setSize(largura, altura);
        container.appendChild(renderer.domElement);
        
        cena.add(new THREE.AmbientLight(0xffffff, 0.6));
        let luz = new THREE.DirectionalLight(0xffffff, 0.8); luz.position.set(10, 15, 10); cena.add(luz);
        
        let cores = [0x8B7355, 0xA0522D, 0xFFD700, 0x696969];
        cores.forEach((cor, i) => {
            let geom = new THREE.BoxGeometry(6, 0.8, 6);
            let mat = new THREE.MeshPhongMaterial({color: cor, transparent: true, opacity: 0.9});
            let bloco = new THREE.Mesh(geom, mat);
            bloco.position.y = 1 - (i * 0.8);
            cena.add(bloco);
        });
        
        function animar() { 
            if (document.getElementById('modal3D').style.display === 'none') return;
            requestAnimationFrame(animar); 
            cena.rotation.y += 0.005; 
            renderer.render(cena, camera); 
        }
        animar();
    }, 200);
}
