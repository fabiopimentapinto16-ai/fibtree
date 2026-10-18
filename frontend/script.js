let map, radarLayers = [], modoAmostra = false, ultimaAnalise = null;
let mapRota, camadaRotaAtual = 'sat', camadaRota = null;

map = L.map('map', {preferCanvas: true}).setView([-15, -50], 4);
L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', { maxZoom: 19 }).addTo(map);

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
    olhoInjetarMelhorias(dados || ultimaAnalise);
    olhoMateriaVisual(dados || ultimaAnalise);
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
            imgEl.alt = 'Ouro Real';
        } else {
            imgEl.src = 'https://images.unsplash.com/photo-1628157588553-5eeea00af15c?q=80&w=400&auto=format&fit=crop';
            imgEl.alt = 'Terras Raras (Bastnasita)';
        }
    }
}

function atualizarListaProcessos(dados) {
    let container = document.getElementById('lista-processos');
    let content = document.getElementById('processos-content');
    if (dados.pontos_sigmine && dados.pontos_sigmine.length > 0) {
        container.style.display = 'block';
        content.innerHTML = dados.pontos_sigmine.slice(0, 20).map(p =>
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
        else { camadaRota = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', { maxZoom: 19 }); alert('Faca uma analise primeiro para ver o calor.'); }
    }
    camadaRota.addTo(mapRota);
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

async function abrir3D() {
    document.getElementById('modal3D').style.display = 'flex';
    let container = document.getElementById('canvas3d');
    container.innerHTML = '<div style="color:#fff; text-align:center; padding-top:100px;">Carregando...</div>';
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
            {profundidade_cm: 0, espessura_cm: 30, tipo: "Solo Orgânico", cor: "#8B7355"},
            {profundidade_cm: 30, espessura_cm: 40, tipo: "Cascalho", cor: "#A0522D"},
            {profundidade_cm: 70, espessura_cm: 50, tipo: "Zona Mineralizada", cor: "#FFD700"},
            {profundidade_cm: 120, espessura_cm: 80, tipo: "Rocha Base", cor: "#696969"}
        ];
    }
    setTimeout(() => {
        container.innerHTML = '';
        let largura = container.clientWidth || 300, altura = container.clientHeight || 300;
        let cena = new THREE.Scene(); cena.background = new THREE.Color(0x020408);
        let camera = new THREE.PerspectiveCamera(45, largura/altura, 0.1, 1000); camera.position.set(8, 6, 10); camera.lookAt(0, 0, 0);
        let renderer = new THREE.WebGLRenderer({antialias: true}); renderer.setSize(largura, altura); container.appendChild(renderer.domElement);
        cena.add(new THREE.AmbientLight(0xffffff, 0.6));
        let luz = new THREE.DirectionalLight(0xffffff, 0.8); luz.position.set(10, 15, 10); cena.add(luz);
        let yAtual = 0, escala = 2;
        let totalAltura = camadas.reduce((acc, c) => acc + (c.espessura_cm / 100) * escala, 0);
        let startY = totalAltura / 2;
        camadas.forEach((c) => {
            let espessura = (c.espessura_cm / 100) * escala;
            let geom = new THREE.BoxGeometry(6, espessura, 6);
            let colorInt = typeof c.cor === 'string' ? parseInt(c.cor.replace('#', '0x')) : c.cor;
            let mat = new THREE.MeshPhongMaterial({color: colorInt, transparent: true, opacity: 0.9});
            let bloco = new THREE.Mesh(geom, mat); bloco.position.y = startY - yAtual - (espessura / 2); cena.add(bloco);
            let edges = new THREE.EdgesGeometry(geom);
            let line = new THREE.LineSegments(edges, new THREE.LineBasicMaterial({color: 0x00f0ff})); line.position.y = bloco.position.y; cena.add(line);
            yAtual += espessura;
        });
        function animar() { if (document.getElementById('modal3D').style.display === 'none') return; requestAnimationFrame(animar); cena.rotation.y += 0.005; renderer.render(cena, camera); }
        animar();
    }, 150);
}


let cprmLayer = null;
function toggleCPRM() {
    if (cprmLayer) {
        map.removeLayer(cprmLayer);
        cprmLayer = null;
        alert('Camada de Falhas CPRM Desativada');
    } else {
        cprmLayer = L.tileLayer.wms('https://geoportal.cprm.gov.br/geoserver/wms', {
            layers: 'geologia:estruturas_lineares',
            format: 'image/png',
            transparent: true,
            opacity: 0.8,
            attribution: 'CPRM'
        }).addTo(map);
        alert('Camada de Falhas CPRM Ativada! Estruturas lineares carregadas diretamente do banco oficial.');
    }
}



// --- INJEÇÃO CIRÚRGICA: IMAGEM DO MINÉRIO E MATA-BITOLA ---
function olhoMateriaVisual(analise) {
    let card = document.getElementById('score-card');
    if (!card) return;
    
    // Remove qualquer imagem de avatar
    card.querySelectorAll('img').forEach(img => {
        if (/avatar|user|perfil|unsplash|pexels|analista|homem|man|person/i.test(img.src + ' ' + img.alt)) {
            img.remove();
        }
    });

    let box = document.getElementById('materia-visual');
    if (!box) {
        box = document.createElement('div');
        box.id = 'materia-visual';
        box.style.cssText = 'margin-top:10px;padding:15px;background:#0a0a0a;border:1px solid #333;border-radius:8px;text-align:center;';
        card.appendChild(box);
    }
    
    let tipo = (analise.tipo_principal || analise.substancia || '').toLowerCase();
    let svg = '', nome = '';
    
    if (tipo.includes('terra') || tipo.includes('rara')) {
        nome = 'TERRAS RARAS'; 
        svg = '<svg width="80" height="80" viewBox="0 0 80 80"><polygon points="30,20 45,15 50,40 35,48" fill="#FF6B9D"/><polygon points="45,25 62,22 65,50 48,55" fill="#4FC3F7"/><polygon points="20,40 35,35 38,62 22,65" fill="#AED581"/></svg>';
    } else if (tipo.includes('ferro')) {
        nome = 'FERRO'; 
        svg = '<svg width="80" height="80" viewBox="0 0 80 80"><polygon points="15,50 25,25 45,18 62,30 65,55 50,68 28,65" fill="#C73E1D"/></svg>';
    } else if (tipo.includes('argila')) {
        nome = 'ARGILA'; 
        svg = '<svg width="80" height="80" viewBox="0 0 80 80"><path d="M20,55 Q18,35 35,25 Q52,18 62,30 Q72,42 65,58 Q55,68 38,65 Q22,62 20,55 Z" fill="#D4B896"/></svg>';
    } else {
        nome = 'OURO'; 
        svg = '<svg width="80" height="80" viewBox="0 0 80 80"><path d="M20,45 Q15,30 30,22 Q45,15 58,22 Q70,30 65,45 Q68,58 55,65 Q40,70 28,63 Q15,58 20,45 Z" fill="#FFD700" stroke="#5C4308" stroke-width="2"/></svg>';
    }
    
    box.innerHTML = `<div style="color:#888;font-size:10px;letter-spacing:1px;margin-bottom:5px;">MATERIAL INDICADO</div><div style="color:#fff;font-weight:bold;margin-bottom:5px;">${nome}</div>${svg}`;

    // A) BLOCO 3D (2 metros acima e camadas)
    let box3d = document.getElementById('bloco-3d-simples');
    if (!box3d) {
        box3d = document.createElement('div');
        box3d.id = 'bloco-3d-simples';
        box3d.style.cssText = 'margin-top:10px;padding:10px;background:#111;border:1px solid #444;border-radius:8px;';
        card.appendChild(box3d);
    }
    
    let score = analise.score_final || 0;
    let profundidade = score > 80 ? 'Raso (0-2m)' : score > 50 ? 'Médio (2-5m)' : 'Profundo (>5m)';
    
    box3d.innerHTML = `
        <div style="color:#00ff88;font-size:11px;font-weight:bold;margin-bottom:5px;">📦 PERFIL 3D ESTIMADO</div>
        <div style="display:flex;justify-content:space-between;font-size:10px;color:#aaa;border-bottom:1px solid #333;padding-bottom:4px;">
            <span>Camada</span><span>Profundidade</span>
        </div>
        <div style="display:flex;justify-content:space-between;font-size:11px;color:#fff;padding:4px 0;">
            <span>Solo</span><span>0m - 0.5m</span>
        </div>
        <div style="display:flex;justify-content:space-between;font-size:11px;color:#FFD700;padding:4px 0;">
            <span>Minério (Estimado)</span><span>${profundidade}</span>
        </div>
        <div style="display:flex;justify-content:space-between;font-size:11px;color:#666;padding:4px 0;">
            <span>Rocha Base</span><span>Abaixo do minério</span>
        </div>
    `;
}



// =========================================================
// INJEÇÃO CIRÚRGICA: IMAGEM DO MINÉRIO, 3D E DETECTORISMO
// =========================================================
function olhoInjetarMelhorias(analise) {
    let card = document.getElementById('score-card');
    if (!card) return;
    
    // --- 1. MATA-BITOLA E IMAGEM DO MINÉRIO ---
    card.querySelectorAll('img').forEach(img => {
        if (/avatar|user|perfil|unsplash|pexels|analista|homem|man|person/i.test((img.src||'') + ' ' + (img.alt||''))) {
            img.remove();
        }
    });

    let box = document.getElementById('materia-visual');
    if (!box) {
        box = document.createElement('div');
        box.id = 'materia-visual';
        box.style.cssText = 'margin-top:10px;padding:15px;background:#0a0a0a;border:1px solid #333;border-radius:8px;text-align:center;';
        card.appendChild(box);
    }
    
    let tipo = ((analise.tipo_principal||'') + ' ' + (analise.substancia||'')).toLowerCase();
    let svg = '', nome = '';
    
    if (tipo.includes('terra') || tipo.includes('rara')) {
        nome = 'TERRAS RARAS'; 
        svg = '<svg width="80" height="80" viewBox="0 0 80 80"><polygon points="30,20 45,15 50,40 35,48" fill="#FF6B9D"/><polygon points="45,25 62,22 65,50 48,55" fill="#4FC3F7"/><polygon points="20,40 35,35 38,62 22,65" fill="#AED581"/></svg>';
    } else if (tipo.includes('ferro')) {
        nome = 'FERRO'; 
        svg = '<svg width="80" height="80" viewBox="0 0 80 80"><polygon points="15,50 25,25 45,18 62,30 65,55 50,68 28,65" fill="#C73E1D"/></svg>';
    } else if (tipo.includes('argila')) {
        nome = 'ARGILA'; 
        svg = '<svg width="80" height="80" viewBox="0 0 80 80"><path d="M20,55 Q18,35 35,25 Q52,18 62,30 Q72,42 65,58 Q55,68 38,65 Q22,62 20,55 Z" fill="#D4B896"/></svg>';
    } else {
        nome = 'OURO'; 
        svg = '<svg width="80" height="80" viewBox="0 0 80 80"><path d="M20,45 Q15,30 30,22 Q45,15 58,22 Q70,30 65,45 Q68,58 55,65 Q40,70 28,63 Q15,58 20,45 Z" fill="#FFD700" stroke="#5C4308" stroke-width="2"/></svg>';
    }
    
    box.innerHTML = `<div style="color:#888;font-size:10px;letter-spacing:1px;margin-bottom:5px;">MATERIAL INDICADO</div><div style="color:#fff;font-weight:bold;margin-bottom:5px;">${nome}</div>${svg}`;

    // --- 2. BLOCO 3D ---
    let box3d = document.getElementById('bloco-3d-simples');
    if (!box3d) {
        box3d = document.createElement('div');
        box3d.id = 'bloco-3d-simples';
        box3d.style.cssText = 'margin-top:10px;padding:10px;background:#111;border:1px solid #444;border-radius:8px;';
        card.appendChild(box3d);
    }
    let score = analise.score_final || 0;
    let profundidade = score > 80 ? 'Raso (0-2m)' : score > 50 ? 'Médio (2-5m)' : 'Profundo (>5m)';
    
    box3d.innerHTML = `
        <div style="color:#00ff88;font-size:11px;font-weight:bold;margin-bottom:5px;">📦 PERFIL 3D ESTIMADO</div>
        <div style="display:flex;justify-content:space-between;font-size:10px;color:#aaa;border-bottom:1px solid #333;padding-bottom:4px;">
            <span>Camada</span><span>Profundidade</span>
        </div>
        <div style="display:flex;justify-content:space-between;font-size:11px;color:#fff;padding:4px 0;">
            <span>Solo</span><span>0m - 0.5m</span>
        </div>
        <div style="display:flex;justify-content:space-between;font-size:11px;color:#FFD700;padding:4px 0;">
            <span>Minério (Estimado)</span><span>${profundidade}</span>
        </div>
    `;

    // --- 3. BOTÃO DO DETECTORISMO ---
    if (!document.getElementById('btn-acionar-detectorismo')) {
        let btnDet = document.createElement('button');
        btnDet.id = 'btn-acionar-detectorismo';
        btnDet.textContent = '🔍 CALCULAR DETECTORISMO (Ouro Superficial)';
        btnDet.style.cssText = 'background:#8B4FA8;color:#fff;font-weight:bold;margin-top:10px;width:100%;padding:12px;border:none;border-radius:8px;cursor:pointer;font-size:13px;display:block;';
        
        btnDet.onclick = async function() {
            btnDet.textContent = '⏳ Analisando Topografia...';
            try {
                let res = await fetch('/api/detectorismo', {
                    method: 'POST', 
                    headers: {'Content-Type': 'application/json'}, 
                    body: JSON.stringify(analise)
                });
                let det = await res.json();
                
                let painel = document.getElementById('painel-detectorismo');
                if (!painel) {
                    painel = document.createElement('div');
                    painel.id = 'painel-detectorismo';
                    painel.style.cssText = 'margin-top:10px;padding:10px;background:#1a2a1a;border:1px solid #00ff88;border-radius:8px;';
                    card.appendChild(painel);
                }
                
                painel.innerHTML = `
                    <div style="text-align:center;margin-bottom:10px;">
                        <div style="font-size:24px;font-weight:bold;color:#00ff88;">${det.score_detector}<span style="font-size:12px;color:#888;">/100</span></div>
                        <div style="font-size:10px;color:#aaa;text-transform:uppercase;">${det.classificacao}</div>
                    </div>
                    <div style="font-size:11px;color:#ccc;">
                        ⛰️ <b>Declive:</b> ${det.declividade_pct !== null ? det.declividade_pct + '%' : 'Indisponível'}<br>
                        💧 <b>Drenagem:</b> ${det.componentes?.drenagem?.motivo || 'N/A'}<br>
                        🪨 <b>Aluvião:</b> ${det.componentes?.aluviao?.motivo || 'N/A'}
                    </div>
                `;
                btnDet.style.display = 'none'; // Esconde o botão após calcular
            } catch (e) {
                btnDet.textContent = '❌ Erro ao calcular. Tente novamente.';
            }
        };
        card.appendChild(btnDet);
    }
}
