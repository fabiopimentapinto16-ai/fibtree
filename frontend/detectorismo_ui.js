(function(){
'use strict';
function criarPainelDetector(){
  if(document.getElementById('painel-detectorismo')) return;
  var p = document.createElement('div');
  p.id = 'painel-detectorismo';
  p.style.cssText = 'position:fixed;top:10px;left:10px;z-index:9999;background:linear-gradient(135deg,#0a0f0a,#0d1a0d);border:2px solid #00ff88;border-radius:12px;padding:15px;font-family:system-ui,sans-serif;box-shadow:0 8px 24px rgba(0,0,0,0.8);max-width:300px;color:#eee;display:none;';
  p.innerHTML = '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;"><b style="color:#00ff88;font-size:14px;">🔍 DETECTORISMO (Ouro Superficial)</b><button onclick="document.getElementById(\\'painel-detectorismo\\').style.display=\\'none\\'" style="background:none;border:none;color:#888;cursor:pointer;font-size:18px;">×</button></div><div id="det-conteudo">Calculando...</div>';
  document.body.appendChild(p);
}

async function calcularDetectorismo(){
  if(!window.ultimaAnalise) return alert("Faça uma análise normal primeiro!");
  criarPainelDetector();
  var p = document.getElementById('painel-detectorismo');
  p.style.display = 'block';
  document.getElementById('det-conteudo').innerHTML = '<div style="text-align:center;color:#888;">⏳ Buscando elevação via Drone...</div>';

  try {
    var r = await fetch('/api/detectorismo', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(window.ultimaAnalise)});
    var d = await r.json();

    var html = '<div style="text-align:center;margin-bottom:15px;">';
    html += '<div style="font-size:32px;font-weight:bold;color:'+(d.score_detector>=75?'#00ff88':'#FFD700')+';">'+d.score_detector+'<span style="font-size:16px;color:#888;">/100</span></div>';
    html += '<div style="font-size:11px;text-transform:uppercase;letter-spacing:1px;color:#aaa;">'+d.classificacao+'</div></div>';

    if(d.declividade_pct !== null) {
       html += '<div style="background:#1a2a1a;padding:8px;border-radius:6px;margin-bottom:10px;font-size:11px;"><b>⛰️ Drone (SRTM):</b> Declive de '+d.declividade_pct+'% nesta área.</div>';
    } else {
       html += '<div style="background:#2a1a1a;padding:8px;border-radius:6px;margin-bottom:10px;font-size:11px;color:#ff8888;"><b>⛰️ Drone:</b> Limite diário atingido ou sem sinal.</div>';
    }

    html += '<div style="font-size:11px;color:#aaa;margin-bottom:5px;"><b>💧 Drenagem:</b> '+(d.componentes?.drenagem?.motivo||'Não avaliado')+'</div>';
    html += '<div style="font-size:11px;color:#aaa;margin-bottom:5px;"><b>🪨 Aluvião:</b> '+(d.componentes?.aluviao?.motivo||'Não avaliado')+'</div>';

    document.getElementById('det-conteudo').innerHTML = html;
  } catch(e) {
    document.getElementById('det-conteudo').innerHTML = '<div style="color:#ff4444;">Erro ao calcular.</div>';
  }
}

function addBotoes(){
  if(document.getElementById('btn-detectorismo')) return;
  var c = document.getElementById('score-card') || document.querySelector('.panel') || document.body;

  // BOTAO DETECTORISMO
  var bDet = document.createElement('button');
  bDet.id='btn-detectorismo'; bDet.textContent='🔍 CALCULAR DETECTORISMO';
  bDet.style.cssText='background:#8B4FA8;color:#fff;font-weight:bold;margin-top:10px;width:100%;padding:12px;border:none;border-radius:8px;cursor:pointer;font-size:14px;display:block;';
  bDet.onclick = calcularDetectorismo;
  c.appendChild(bDet);

  // BOTAO EXPORTAR BACKTEST
  var bExp = document.createElement('button');
  bExp.id='btn-exportar'; bExp.textContent='💾 EXPORTAR MEUS ACHADOS (CSV)';
  bExp.style.cssText='background:#17a2b8;color:#fff;font-weight:bold;margin-top:10px;width:100%;padding:12px;border:none;border-radius:8px;cursor:pointer;font-size:14px;display:block;';
  bExp.onclick = function(){
    var db = JSON.parse(localStorage.getItem('backtest_olho_deus') || '[]');
    if(db.length === 0) return alert("Você ainda não registrou nenhum achado no campo.");
    var csv = "Latitude,Longitude,Score,Encontrou_Ouro,Data\n";
    db.forEach(function(p) { csv += p.lat+","+p.lng+","+p.score+","+(p.achou_ouro?"SIM":"NAO")+","+p.data+"\n"; });
    var blob = new Blob([csv], {type: 'text/csv;charset=utf-8;'});
    var a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = 'backtest_achados.csv'; a.click();
  };
  c.appendChild(bExp);
}

document.addEventListener('DOMContentLoaded', addBotoes);
})();