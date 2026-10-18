(function(){
function matarBitola(){
  var c = document.getElementById('score-card'); if(!c) return;
  c.querySelectorAll('img').forEach(function(img){
    if(/avatar|user|perfil|unsplash|pexels|analista|homem|man|person/.test((img.src+img.alt).toLowerCase())) img.remove();
  });
  var box = document.getElementById('materia-visual');
  if(!box){ box = document.createElement('div'); box.id='materia-visual'; box.style.cssText='margin-top:10px;padding:10px;background:#1a1a1a;border-radius:8px;text-align:center;'; c.appendChild(box); }
  if(box.innerHTML.trim() === '' || box.innerHTML.indexOf('svg') === -1){
    var tipo = window.ultimaAnalise && window.ultimaAnalise.tipo_principal ? window.ultimaAnalise.tipo_principal.toLowerCase() : '';
    if(tipo.indexOf('terra')>-1 || tipo.indexOf('rara')>-1) box.innerHTML = '<div style="color:#ff6b9d;font-weight:bold;">TERRAS RARAS</div><svg width="60" height="60" viewBox="0 0 80 80"><polygon points="30,20 45,15 50,40 35,48" fill="#FF6B9D"/><polygon points="45,25 62,22 65,50 48,55" fill="#4FC3F7"/></svg>';
    else box.innerHTML = '<div style="color:#FFD700;font-weight:bold;">OURO</div><svg width="60" height="60" viewBox="0 0 80 80"><path d="M20,45 Q15,30 30,22 Q45,15 58,22 Q70,30 65,45 Q68,58 55,65 Q40,70 28,63 Q15,58 20,45 Z" fill="#FFD700" stroke="#5C4308" stroke-width="2"/></svg>';
  }
}
document.addEventListener('DOMContentLoaded', function(){
  matarBitola();
  var c = document.getElementById('score-card');
  if(c && window.MutationObserver) new MutationObserver(matarBitola).observe(c,{childList:true,subtree:true});
});
})();