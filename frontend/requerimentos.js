(function(){
function addBotoes(){
  if(document.getElementById('btn-req-anm')) return;
  var c = document.getElementById('score-card') || document.querySelector('.panel') || document.body;

  // Botão ANM
  var bReq = document.createElement('button');
  bReq.id='btn-req-anm'; bReq.textContent='📝 GERAR REQUERIMENTO ANM';
  bReq.style.cssText='background:#00ff88;color:#000;font-weight:bold;margin-top:10px;width:100%;padding:12px;border:none;border-radius:8px;cursor:pointer;font-size:14px;display:block;';
  bReq.onclick = async function(){
    if(!window.ultimaAnalise) return alert("Faça uma análise primeiro!");
    bReq.textContent = '⏳ Gerando...';
    var payload = Object.assign({}, window.ultimaAnalise, {requerimento:{tipo:'pesquisa',tipo_nome:'Pesquisa Mineral',nome:'Requerente',cpf:'000',substancia:'OURO',area_ha:'1000'}});
    try {
      var r = await fetch('/api/requerimento-completo',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
      var blob = await r.blob(); var a = document.createElement('a'); a.href=URL.createObjectURL(blob); a.download='Requerimento_ANM.pdf'; a.click();
      bReq.textContent = '✅ PDF Baixado!'; setTimeout(()=>bReq.textContent='📝 GERAR REQUERIMENTO ANM', 3000);
    } catch(e){ alert('Erro'); bReq.textContent='📝 GERAR REQUERIMENTO ANM'; }
  };
  c.appendChild(bReq);

  // Botão Espiral
  var bFib = document.createElement('button');
  bFib.id='btn-fibonacci'; bFib.textContent='🌀 MARCAR ESPIRAL FIBONACCI';
  bFib.style.cssText='background:#007BFF;color:#fff;font-weight:bold;margin-top:10px;width:100%;padding:12px;border:none;border-radius:8px;cursor:pointer;font-size:14px;display:block;';
  bFib.onclick = async function(){
    if(!window.ultimaAnalise) return alert("Faça uma análise primeiro!");
    bFib.textContent = '⏳ Desenhando...';
    var coord = window.ultimaAnalise.coordenada || window.ultimaAnalise.ponto_interesse;
    try {
      var r = await fetch('/api/detectorismo',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({coordenada: coord})});
      var det = await r.json();
      if(det.espiral_fibonacci && window.map) {
        det.espiral_fibonacci.forEach((p, i) => L.circleMarker([p.lat, p.lng], {radius:5, color:'#FFD700', fillOpacity:0.8}).addTo(window.map).bindPopup('Ponto '+(i+1)));
        bFib.textContent = '✅ Espiral Marcada!'; setTimeout(()=>bFib.textContent='🌀 MARCAR ESPIRAL FIBONACCI', 3000);
      }
    } catch(e){ bFib.textContent='🌀 MARCAR ESPIRAL FIBONACCI'; }
  };
  c.appendChild(bFib);

  // NOVO: Botão de Validação de Campo
  var bVal = document.createElement('button');
  bVal.id='btn-val-campo'; bVal.textContent='🎯 REGISTRAR ACHADO NO CAMPO';
  bVal.style.cssText='background:#FF9800;color:#fff;font-weight:bold;margin-top:10px;width:100%;padding:12px;border:none;border-radius:8px;cursor:pointer;font-size:14px;display:block;';
  bVal.onclick = function(){
    if(!window.ultimaAnalise) return alert("Faça uma análise primeiro!");
    var achou = confirm("O detector apitou e você cavou? (OK = Sim, Cancelar = Não)");
    var coord = window.ultimaAnalise.coordenada || window.ultimaAnalise.ponto_interesse;
    if(!coord) return;
    var db = JSON.parse(localStorage.getItem('backtest_olho_deus') || '[]');
    db.push({lat: coord.lat, lng: coord.lng, score: window.ultimaAnalise.score_final, achou_ouro: achou, data: new Date().toISOString()});
    localStorage.setItem('backtest_olho_deus', JSON.stringify(db));
    alert("✅ Achado registrado! Total: " + db.length + " pontos validados.");
  };
  c.appendChild(bVal);
}
document.addEventListener('DOMContentLoaded', addBotoes);
})();