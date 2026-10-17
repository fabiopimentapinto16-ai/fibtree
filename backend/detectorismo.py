import math, requests
from flask import Blueprint, request, jsonify
bp_detector = Blueprint("detectorismo", __name__)
def _elevacoes(lat, lng):
    dlat=1.0/111.0; dlng=1.0/(111.0*math.cos(math.radians(lat)) or 1e-6)
    pts=[(lat,lng),(lat+dlat,lng),(lat-dlat,lng),(lat,lng+dlng),(lat,lng-dlng)]
    try:
        locs=[{"latitude":la,"longitude":lo} for la,lo in pts]
        r=requests.post("https://api.open-elevation.com/api/v1/lookup", json={"locations":locs}, timeout=10)
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
    return jsonify({"score_detector": 85 if decl else 50, "classificacao": "PROPÍCIO" if decl else "MODERADO", "declividade_pct": decl})
