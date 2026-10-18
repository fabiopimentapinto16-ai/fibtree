(function(){
'use strict';

// Função que resolve o problema: pega a variável do jeito que o seu script antigo salvou
function getDadosAnalise(){
  try {
    if (typeof ultimaAnalise !== 'undefined' && ultimaAnalise !== null) return ultimaAnalise;
  } catch(e) {}
  if (window.ultimaAnalise) return window.ultimaAnalise;
  try {
    var ls = localStorage.getItem('ultimaAnalise');
    if (ls) return JSON.parse(ls);
  } catch(e) {}
  return null;
}

// 1. Mata-Bitola (Injeta a imagem correta)
function checarScore(){
  var c = document.getElementById('score-card');
  if(!c) return;
  
  // Remove foto de avatar
  c.querySelectorAll('img').forEach(function(img){
    var s = (img.src + ' ' + img.alt).toLowerCase();
    if(/avatar|user|perfil|unsplash|pexels|analista|homem|man|person/.test(s)) img.remove();
  });

  // Desenha o SVG se estiver vazio
  var box = document.getElementById('materia-visual');
  if(!box) {
    box = document.createElement('div'); box.id='materia-visual';
    box.style.cssText='margin-top:10px;padding:10px;background:#1a1a1a;border-radius:8px;text-align:center;';
    c.appendChild(box);
  }
  if(box.innerHTML.trim() === '' || box.innerHTML.indexOf('svg') === -1){
    var a = getDadosAnalise();
    var tipo = a && a.tipo_principal ? a.tipo_principal.toLowerCase() : '';
    if(tipo.indexOf('terra')>-1 || tipo.indexOf('rara')>-1) {
      box.innerHTML = '<div style="color:#ff6b9d;font-weight:bold;">TERRAS RARAS</div><svg width="60" height="60" viewBox="0 0 80 80"><polygon points="30,20 45,15 50,40 35,48" fill="#FF6B9D"/><polygon points="45,25 62,22 65,50 48,55" fill="#4FC3F7"/><polygon points="20,40 35,35 38,62 22,65" fill="#AED581"/></svg>';
    } else {
      box.innerHTML = '<div style="color:#FFD700;font-weight:bold;">OURO</div><svg width="60" height="60" viewBox="0 0 80 80"><path d="M20,45 Q15,30 30,22 Q45,15 58,22 Q70,30 65,45 Q68,58 55,65 Q40,70 28,63 Q15,58 20,45 Z" fill="#FFD700" stroke="#5C4308" stroke-width="2"/></svg>';
    }
  }
}

// 2. Botões Novos (com leitura correta dos dados)
function addBotoes(){
  if(document.getElementById('btn-detectorismo')) return;
  
  var c = document.getElementById('score-card') || document.querySelector('.panel');
  if(!c) { setTimeout(addBotoes, 1000); return; } // Se o painel ainda não carregou, tenta de novo

  // Botão Detectorismo
  var bDet = document.createElement('button');
  bDet.id='btn-detectorismo'; bDet.textContent='🔍 CALCULAR DETECTORISMO';
  bDet.style.cssText='background:#8B4FA8;color:#fff;font-weight:bold;margin-top:10px;width:100%;padding:12px;border:none;border-radius:8px;cursor:pointer;font-size:14px;display:block;';
  bDet.onclick = async function(){
    var dados = getDadosAnalise();
    if(!dados) return alert("Faça uma análise primeiro!");
    bDet.textContent = '⏳ Calculando Drone...';
    try {
      var r = await fetch('/api/detectorismo',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(dados)});
      var d = await r.json();
      var msg = "SCORE DETECTOR: " + d.score_detector + "/100\n" + d.classificacao;
      if(d.declividade_pct !== null) msg += "\nDeclive (Drone): " + d.declividade_pct + "%";
      alert(msg);
      bDet.textContent = '🔍 CALCULAR DETECTORISMO';
    } catch(e){ alert('Erro no servidor'); bDet.textContent='🔍 CALCULAR DETECTORISMO'; }
  };
  c.appendChild(bDet);

  // Botão Espiral
  var bFib = document.createElement('button');
  bFib.id='btn-fibonacci'; bFib.textContent='🌀 MARCAR ESPIRAL FIBONACCI';
  bFib.style.cssText='background:#007BFF;color:#fff;font-weight:bold;margin-top:10px;width:100%;padding:12px;border:none;border-radius:8px;cursor:pointer;font-size:14px;display:block;';
  bFib.onclick = async function(){
    var dados = getDadosAnalise();
    if(!dados) return alert("Faça uma análise primeiro!");
    bFib.textContent = '⏳ Desenhando...';
    try {
      var r = await fetch('/api/detectorismo',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(dados)});
      var det = await r.json();
      var map = window.map || (typeof map !== 'undefined' ? map : null);
      if(det.espiral_fibonacci && map) {
        det.espiral_fibonacci.forEach((p, i) => L.circleMarker([p.lat, p.lng], {radius:5, color:'#FFD700', fillOpacity:0.8}).addTo(map).bindPopup('Ponto '+(i+1)));
        bFib.textContent = '✅ Espiral Marcada!'; setTimeout(()=>bFib.textContent='🌀 MARCAR ESPIRAL FIBONACCI', 3000);
      } else { alert("Mapa não encontrado."); bFib.textContent='🌀 MARCAR ESPIRAL FIBONACCI'; }
    } catch(e){ alert('Erro'); bFib.textContent='🌀 MARCAR ESPIRAL FIBONACCI'; }
  };
  c.appendChild(bFib);

  // Botão Validação
  var bVal = document.createElement('button');
  bVal.id='btn-val-campo'; bVal.textContent='🎯 REGISTRAR ACHADO NO CAMPO';
  bVal.style.cssText='background:#FF9800;color:#fff;font-weight:bold;margin-top:10px;width:100%;padding:12px;border:none;border-radius:8px;cursor:pointer;font-size:14px;display:block;';
  bVal.onclick = function(){
    var dados = getDadosAnalise();
    if(!dados) return alert("Faça uma análise primeiro!");
    var achou = confirm("O detector apitou e você cavou? (OK = Sim, Cancelar = Não)");
    var coord = dados.coordenada || dados.ponto_interesse;
    if(!coord) return;
    var db = JSON.parse(localStorage.getItem('backtest_olho_deus') || '[]');
    db.push({lat: coord.lat, lng: coord.lng, score: dados.score_final, achou_ouro: achou, data: new Date().toISOString()});
    localStorage.setItem('backtest_olho_deus', JSON.stringify(db));
    alert("✅ Achado registrado!");
  };
  c.appendChild(bVal);
}

document.addEventListener('DOMContentLoaded', function(){
  checarScore();
  addBotoes();
  var c = document.getElementById('score-card');
  // Observa a tela. Toda vez que você clicar em ANALISAR POTENCIAL, ele roda as funções de novo
  if(c && window.MutationObserver) new MutationObserver(function(){
    checarScore();
    addBotoes();
  }).observe(c,{childList:true,subtree:true});
});
})();