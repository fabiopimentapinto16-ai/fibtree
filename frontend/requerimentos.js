(function(){
'use strict';
function addBotao(){
  if(document.getElementById('btn-req-anm')) return;
  var b = document.createElement('button');
  b.id='btn-req-anm'; b.textContent='📝 GERAR REQUERIMENTO ANM';
  b.style.cssText='background:#00ff88;color:#000;font-weight:bold;margin-top:10px;width:100%;padding:12px;border:none;border-radius:8px;cursor:pointer;font-size:14px;display:block;box-shadow:0 4px 12px rgba(0,255,136,0.3);';
  b.onclick = async function(){
    if(!window.ultimaAnalise) return alert("Faça uma análise primeiro!");
    b.textContent = '⏳ Gerando PDF...';
    var payload = Object.assign({}, window.ultimaAnalise, {
      requerimento: { tipo:'pesquisa', tipo_nome:'Pesquisa Mineral', tipo_art:'Art. 15', nome:'Requerente', cpf:'000.000.000-00', substancia:'OURO', area_ha:'1000' }
    });
    try {
      var r = await fetch('/api/requerimento-completo',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
      if(!r.ok) throw new Error('Erro '+r.status);
      var blob = await r.blob(); var url = URL.createObjectURL(blob);
      var a = document.createElement('a'); a.href=url; a.download='Requerimento_ANM.pdf'; a.click();
      b.textContent = '✅ PDF Baixado!'; setTimeout(()=>{ b.textContent='📝 GERAR REQUERIMENTO ANM'; }, 3000);
    } catch(e){ alert('Erro: '+e.message); b.textContent='📝 GERAR REQUERIMENTO ANM'; }
  };
  var c = document.getElementById('score-card') || document.querySelector('.panel') || document.body;
  c.appendChild(b);
}
document.addEventListener('DOMContentLoaded', addBotao);
})();