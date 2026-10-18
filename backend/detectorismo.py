import math, requests, os
from flask import Blueprint, request, jsonify
bp_detector = Blueprint("detectorismo", __name__)

def _elevacoes(lat, lng):
    dlat=1.0/111.0; dlng=1.0/(111.0*math.cos(math.radians(lat)) or 1e-6)
    pts=[(lat,lng),(lat+dlat,lng),(lat-dlat,lng),(lat,lng+dlng),(lat,lng-dlng)]
    
    # 1. Tenta OpenTopography (SRTM 30m) se a chave estiver configurada
    topo_key = os.environ.get("OPENTOPO_API_KEY", "").strip()
    if topo_key:
        try:
            locs = "|".join(f"{la},{lo}" for la,lo in pts)
            r = requests.get(f"https://portal.opentopography.org/API/globaldem?demtype=SRTMGL1&locations={locs}&API_Key={topo_key}", timeout=8)
            if r.status_code == 200:
                data = r.json()
                # A API retorna uma lista de resultados
                if "results" in data:
                    return [pt.get("elevation") for pt in data["results"]]
        except Exception: pass
        
    # 2. Fallback: Open-Elevation (Grátis, sem chave)
    try:
        locs=[{"latitude":la,"longitude":lo} for la,lo in pts]
        r=requests.post("https://api.open-elevation.com/api/v1/lookup", json={"locations":locs}, timeout=8)
        if r.status_code==200: return [it["elevation"] for it in r.json()["results"]]
    except: pass
    return None

@bp_detector.route("/api/detectorismo", methods=["POST"])
def detectorismo():
    d=request.get_json(silent=True) or {}
    coord=d.get("coordenada") or d.get("ponto_interesse") or {}
    lat=coord.get("lat"); lng=coord.get("lng")
    if lat is None: return jsonify({"erro":"coordenada"}),400
    
    els = _elevacoes(lat, lng); decl = None
    if els and len(els)>=5:
        dmax=max(abs(els[0]-els[1]),abs(els[0]-els[2]),abs(els[0]-els[3]),abs(els[0]-els[4]))
        decl = round(100.0 * dmax / 1000.0, 2)
        
    # Espiral Fibonacci
    angulo_ouro = 2.399963229728653
    pontos_fib = []
    for i in range(1, 11):
        r = math.sqrt(i) * 0.0005
        theta = i * angulo_ouro
        p_lat = lat + (r * math.sin(theta) / 111.0)
        p_lng = lng + (r * math.cos(theta) / (111.0 * math.cos(math.radians(lat))))
        pontos_fib.append({"lat": round(p_lat, 6), "lng": round(p_lng, 6)})
        
    return jsonify({
        "score_detector": 85 if decl else 50, 
        "classificacao": "PROPÍCIO" if decl else "MODERADO", 
        "declividade_pct": decl,
        "espiral_fibonacci": pontos_fib
    })
