let map, radarLayers = [], modoAmostra = false, ultimaAnalise = null;
let mapRota, camadaRotaAtual = 'sat', camadaRota = null;
let cena3D, camera3D, renderer3D, raycaster, mouse, blocos3D = [];

map = L.map('map', {preferCanvas: true}).setView([-15, -50], 4);
const camadaSat = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', { maxZoom: 19 }).addTo(map);

L.control.scale({imperial: false}).addTo(map);
L.control.fullscreen({ position: 'topleft' }).addTo(map);

map.on('click', function(e) {
    let lat = e.latlng.lat.toFixed(6), lng = e.latlng.lng.toFixed(6);
    document.getElementById('lat').value = lat; document.getElementById('lng').value = lng;
    if (modoAmostra) { L.marker([lat, lng]).addTo(map).bindPopup('Amostra Salva').openPopup(); modoAmostra = false; return; }
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
        desenharRadar(lat, lng); desenharPontosAnalise(dados); atualizarScore(dados); atualizarListaProcessos(dados);
        let hist = JSON.parse(localStorage.getItem('historico') || '[]'); 
        hist.push({lat, lng, score: dados.score_final, data: new Date().toISOString(), dados}); 
        localStorage.setItem('historico', JSON.stringify(hist));
        ultimaAnalise = dados;
    } catch (e) { alert('Erro: ' + e.message); }
    btn.innerText = '🔍 ANALISAR POTENCIAL';
}

function atualizarScore(dados) {
    let card = document.getElementById('score-card');
    card.style.display = 'block';
    document.getElementById('score-value').innerText = dados.score_final;
    document.getElementById('score-classif').innerText = dados.classificacao;
    document.getElementById('score-type').innerText = dados.tipo_principal === 'ouro' ? 'OURO 🥇' : 'TERRAS RARAS 💎';
    document.getElementById('score-breakdown').innerText = `Ouro: ${dados.score_ouro} | ETR: ${dados.score_etr}`;
    let cor = dados.score_final >= 70 ? '#00ff88' : dados.score_final >= 45 ? '#ffcc00' : '#ff3355';
    card.style.borderColor = cor; document.querySelector('.score-circle').style.borderColor = cor; document.getElementById('score-value').style.color = cor;

    let imgEl = document.getElementById('mineral-image');
    if (imgEl) {
        imgEl.style.display = 'block';
        if (dados.tipo_principal === 'ouro') {
            imgEl.src = 'https://images.unsplash.com/photo-1610375461246-83df859d849d?q=80&w=400&auto=format&fit=crop';
            imgEl.alt = 'Minério de Ouro Real';
        } else {
            imgEl.src = 'https://images.unsplash.com/photo-1628157588553-5eeea00af15c?q=80&w=400&auto=format&fit=crop';
            imgEl.alt = 'Minério de Terras Raras';
        }
    }
}

function atualizarListaProcessos(dados) {
    let container = document.getElementById('lista-processos');
    let content = document.getElementById('processos-content');
    if (dados.pontos_sigmine && dados.pontos_sigmine.length > 0) {
        container.style.display = 'block';
        content.innerHTML = dados.pontos_sigmine.slice(0, 15).map(p => 
            `<div class="processo-item"><strong>${p.processo}</strong><br>${p.subs || 'N/I'} (${p.fase || 'N/I'})<br>Distância: ${p.distancia_km} km</div>`
        ).join('');
    } else { container.style.display = 'none'; }
}

function desenharPontosAnalise(dados) {
    if (dados.pontos_sigmine) {
        if (window.sigmineCluster) map.removeLayer(window.sigmineCluster);
        window.sigmineCluster = L.markerClusterGroup();
        dados.pontos_sigmine.forEach(p => {
            let popupHTML = `<b>Processo:</b> ${p.processo}<br><b>Mineral:</b> ${p.subs || 'N/I'}<br><b>Fase:</b> ${p.fase || 'N/I'}<br>
                             <button onclick="criarRota(${p.lat}, ${p.lng})" style="margin-top:8px; padding:8px; background:#ff6400; color:#fff; border:none; border-radius:4px; font-weight:bold; width:100%; cursor:pointer;">🛣️ CRIAR ROTA</button>`;
            window.sigmineCluster.addLayer(L.circleMarker([p.lat, p.lng], {color: '#00ff88', radius: 5, fillOpacity: 0.9, weight: 2}).bindPopup(popupHTML));
        });
        map.addLayer(window.sigmineCluster);
    }
    if (dados.ponto_interesse) {
        const pi = dados.ponto_interesse;
        const corPonto = dados.tipo_principal === 'ouro' ? '#FFD700' : '#00FFFF';
        const titulo = dados.tipo_principal === 'ouro' ? '⛏️ PONTO DE DETECTORISMO' : '🎯 PONTO DE INTERESSE';
        let popupHTML = `<b style="color:${corPonto};">${titulo}</b><br><b>Score:</b> ${pi.score}%<br><b>Motivo:</b> ${pi.motivo || 'Alta probabilidade'}<br>
                         <button onclick="criarRota(${pi.lat}, ${pi.lng})" style="margin-top:8px; padding:10px; background:#ff6400; color:#fff; border:none; border-radius:4px; font-weight:bold; width:100%; cursor:pointer;">🛣️ CRIAR ROTA</button>`;
        L.circleMarker([pi.lat, pi.lng], {color: corPonto, radius: 10, fillOpacity: 1, weight: 3}).addTo(map).bindPopup(popupHTML).openPopup();
    }
}

function criarRota(destLat, destLng) {
    if (!navigator.geolocation) { alert('GPS não suportado.'); return; }
    navigator.geolocation.getCurrentPosition(function(pos) {
        window.open(`https://www.google.com/maps/dir/?api=1&origin=${pos.coords.latitude},${pos.coords.longitude}&destination=${destLat},${destLng}&travelmode=driving`, '_blank');
    }, function(err) { alert('Erro no GPS: ' + err.message); }, { enableHighAccuracy: true, timeout: 15000 });
}

async function abrir3D() {
    document.getElementById('modal3D').style.display = 'flex';
    document.getElementById('layer-info').style.display = 'none'; 
    
    let container = document.getElementById('canvas3d');
    container.innerHTML = '<div style="color:#fff; text-align:center; padding-top:100px;">Carregando simulação...</div>';

    let camadas = [];
    try {
        if (ultimaAnalise) {
            let res = await fetch('/api/simular-subsolo', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({lat: ultimaAnalise.coordenada.lat, lng: ultimaAnalise.coordenada.lng, resultado_analise: ultimaAnalise}) });
            let dadosSim = await res.json();
            camadas = dadosSim.camadas || [];
        }
    } catch(e) { console.warn(e); }

    if (camadas.length === 0) {
        camadas = [
            {profundidade_cm: 0, espessura_cm: 30, tipo: "Solo Orgânico", cor: "#8B7355", descricao: "Camada superficial com matéria orgânica e raízes."},
            {profundidade_cm: 30, espessura_cm: 40, tipo: "Cascalho Aluvionar", cor: "#A0522D", descricao: "Zona de aluvião! Ideal para detector de metais encontrar pepitas de ouro."},
            {profundidade_cm: 70, espessura_cm: 50, tipo: "Zona Mineralizada", cor: "#FFD700", descricao: "Concentração de óxido de ferro ou argila. Alta probabilidade de minério."},
            {profundidade_cm: 120, espessura_cm: 80, tipo: "Rocha Base", cor: "#696969", descricao: "Rocha sã ou saprolito. Requer britagem para extração em rocha dura."}
        ];
    }

    setTimeout(() => {
        container.innerHTML = '';
        let largura = container.clientWidth || 300, altura = container.clientHeight || 300;
        cena3D = new THREE.Scene(); cena3D.background = new THREE.Color(0x020408);
        camera3D = new THREE.PerspectiveCamera(45, largura/altura, 0.1, 1000); camera3D.position.set(8, 6, 10); camera3D.lookAt(0, 0, 0);
        renderer3D = new THREE.WebGLRenderer({antialias: true}); renderer3D.setSize(largura, altura); container.appendChild(renderer3D.domElement);
        
        cena3D.add(new THREE.AmbientLight(0xffffff, 0.6));
        let luz = new THREE.DirectionalLight(0xffffff, 0.8); luz.position.set(10, 15, 10); cena3D.add(luz);
        
        let yAtual = 0, escala = 2;
        let totalAltura = camadas.reduce((acc, c) => acc + (c.espessura_cm / 100) * escala, 0);
        let startY = totalAltura / 2;
        
        blocos3D = []; 

        camadas.forEach((c) => {
            let espessura = (c.espessura_cm / 100) * escala;
            let geom = new THREE.BoxGeometry(6, espessura, 6);
            let colorInt = typeof c.cor === 'string' ? parseInt(c.cor.replace('#', '0x')) : c.cor;
            let mat = new THREE.MeshPhongMaterial({color: colorInt, transparent: true, opacity: 0.9});
            let bloco = new THREE.Mesh(geom, mat);
            bloco.position.y = startY - yAtual - (espessura / 2);
            
            bloco.userData = {
                titulo: c.tipo,
                profundidade: `${c.profundidade_cm}cm a ${c.profundidade_cm + c.espessura_cm}cm`,
                descricao: c.descricao || "Sem descrição adicional."
            };
            
            cena3D.add(bloco);
            blocos3D.push(bloco); 
            
            let edges = new THREE.EdgesGeometry(geom);
            let line = new THREE.LineSegments(edges, new THREE.LineBasicMaterial({color: 0x00f0ff}));
            line.position.y = bloco.position.y;
            cena3D.add(line);
            yAtual += espessura;
        });

        raycaster = new THREE.Raycaster();
        mouse = new THREE.Vector2();
        
        renderer3D.domElement.addEventListener('click', (event) => {
            const rect = renderer3D.domElement.getBoundingClientRect();
            mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
            mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

            raycaster.setFromCamera(mouse, camera3D);
            const intersects = raycaster.intersectObjects(blocos3D);

            if (intersects.length > 0) {
                const data = intersects[0].object.userData;
                document.getElementById('layer-info').style.display = 'block';
                document.getElementById('info-title').innerText = `${data.titulo} (${data.profundidade})`;
                document.getElementById('info-desc').innerText = data.descricao;
            }
        });

        function animar() { 
            if (document.getElementById('modal3D').style.display === 'none') return;
            requestAnimationFrame(animar); 
            cena3D.rotation.y += 0.005; 
            renderer3D.render(cena3D, camera3D); 
        }
        animar();
    }, 150);
}

function fecharModal(id) { document.getElementById(id).style.display = 'none'; }
function criarRotaGoogleMaps() { if (!ultimaAnalise) return alert('Faça uma análise primeiro'); criarRota(ultimaAnalise.coordenada.lat, ultimaAnalise.coordenada.lng); }
function ativarDetectorismo() { if (!ultimaAnalise) return alert('Faça uma análise primeiro.'); const pi = ultimaAnalise.ponto_interesse; if (pi) criarRota(pi.lat, pi.lng); else alert('Nenhum ponto ideal encontrado.'); }
function gerarPDF() { if(!ultimaAnalise) return alert('Analise primeiro'); fetch('/api/gerar-pdf', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(ultimaAnalise) }).then(r=>r.blob()).then(b => { let a = document.createElement('a'); a.href = URL.createObjectURL(b); a.download = 'relatorio.pdf'; a.click(); }); }
function gerarMemorial() { if(!ultimaAnalise) return alert('Analise primeiro'); fetch('/api/gerar-memorial', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(ultimaAnalise) }).then(r=>r.blob()).then(b => { let a = document.createElement('a'); a.href = URL.createObjectURL(b); a.download = 'memorial.pdf'; a.click(); }); }
function exportarKML() { if(!ultimaAnalise) return alert('Analise primeiro'); fetch('/api/exportar-kml', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(ultimaAnalise) }).then(r=>r.blob()).then(b => { let a = document.createElement('a'); a.href = URL.createObjectURL(b); a.download = 'mapa.kml'; a.click(); }); }
function abrirHistorico() { let h = JSON.parse(localStorage.getItem('historico') || '[]'); document.getElementById('listaHistorico').innerHTML = h.length ? h.map(x => '<div style="border-bottom:1px solid #333; padding:10px;">Lat: ' + x.lat + ' | Score: ' + x.score + '</div>').join('') : '<p>Vazio</p>'; document.getElementById('modalHistorico').style.display = 'flex'; }
function exportarCSV() { let h = JSON.parse(localStorage.getItem('historico') || '[]'); if(!h.length) return; let a = document.createElement('a'); a.href = URL.createObjectURL(new Blob(['Lat,Lng,Score\n' + h.map(x => x.lat + ',' + x.lng + ',' + x.score).join('\n')], {type: 'text/csv'})); a.download = 'hist.csv'; a.click(); }
function ativarModoAmostra() { modoAmostra = true; alert('Clique no mapa para marcar a amostra.'); }
function ativarGPS() { navigator.geolocation.getCurrentPosition(p => { document.getElementById('lat').value = p.coords.latitude.toFixed(6); document.getElementById('lng').value = p.coords.longitude.toFixed(6); map.setView([p.coords.latitude, p.coords.longitude], 13); }); }
function abrirModalRota() {
    document.getElementById('modalRota').style.display = 'flex';
    setTimeout(() => {
        if (!mapRota) {
            mapRota = L.map('mapRota', {preferCanvas: true}).setView([-15, -50], 4);
            camadaRota = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', { maxZoom: 19 }).addTo(mapRota);
            if (ultimaAnalise) { L.marker([ultimaAnalise.coordenada.lat, ultimaAnalise.coordenada.lng]).addTo(mapRota); mapRota.setView([ultimaAnalise.coordenada.lat, ultimaAnalise.coordenada.lng], 12); }
        }
        mapRota.invalidateSize();
    }, 200);
}
function trocarCamadaRota(tipo) {
    if (!mapRota) return;
    mapRota.removeLayer(camadaRota);
    if (tipo === 'sat') camadaRota = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', { maxZoom: 19 });
    else if (tipo === 'falsecolor') camadaRota = L.tileLayer('https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_CorrectedReflectance_Bands721/default/2023-10-01/GoogleMapsCompatible_Level9/{z}/{y}/{x}.jpg', { maxZoom: 9, opacity: 0.9 });
    else if (tipo === 'heat') {
        if (ultimaAnalise && ultimaAnalise.pontos_sigmine) camadaRota = L.heatLayer(ultimaAnalise.pontos_sigmine.map(p => [p.lat, p.lng, 0.8]), {radius: 25, blur: 15, maxZoom: 17});
        else { camadaRota = camadaSat; alert('Faça uma análise primeiro.'); }
    }
    camadaRota.addTo(mapRota);
}
