import math, os, json

REGIOES = [
    {"nome": "Serra dos Carajas", "lat": -6.0, "lng": -50.0, "raio": 2.0, "tipo": "ouro", "facilidade": "media"},
    {"nome": "Cumaru", "lat": -6.5, "lng": -50.5, "raio": 1.0, "tipo": "ouro", "facilidade": "facil"},
    {"nome": "Serra Pelada", "lat": -5.9, "lng": -49.6, "raio": 0.8, "tipo": "ouro", "facilidade": "dificil"},
    {"nome": "Pocos de Caldas", "lat": -21.8, "lng": -46.5, "raio": 0.8, "tipo": "ETR", "facilidade": "media"}
]

DADOS_SIGMINE = []
_caminho_json = os.path.join(os.path.dirname(__file__), "dados_sigmine.json")
if os.path.exists(_caminho_json):
    try:
        with open(_caminho_json, "r", encoding="utf-8") as _f:
            DADOS_SIGMINE = json.load(_f)
    except Exception as _e:
        print(f"Erro ao carregar SIGMINE: {_e}")

def calcular_distancia_km(lat1, lng1, lat2, lng2):
    R = 6371.0
    d_lat = math.radians(lat2 - lat1)
    d_lng = math.radians(lng2 - lng1)
    a = math.sin(d_lat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lng/2)**2
    return R * 2 * math.asin(math.sqrt(a))

def calcular_score(lat, lng):
    score_ouro = 10
    score_etr = 10
    evidencias_ouro = []
    evidencias_etr = []
    
    # 1. Busca por depósitos conhecidos (raio de 5km)
    pontos_proximos = []
    for r in REGIOES:
        dist = calcular_distancia_km(lat, lng, r["lat"], r["lng"])
        if dist <= 5.0:
            pontos_proximos.append({
                "nome": r["nome"],
                "tipo": r["tipo"],
                "distancia_km": round(dist, 2),
                "lat": r["lat"],
                "lng": r["lng"],
                "facilidade": r["facilidade"]
            })
            peso = 50 if dist < 1 else (30 if dist < 3 else 15)
            if r["tipo"] == "ouro":
                score_ouro += peso
                evidencias_ouro.append(f"Proximidade de {r['nome']} ({dist:.1f} km)")
            else:
                score_etr += peso
                evidencias_etr.append(f"Proximidade de {r['nome']} ({dist:.1f} km)")
                
    # 2. Varredura SIGMINE (270.000 processos)
    pontos_sigmine = []
    for s in DADOS_SIGMINE:
        dist_s = calcular_distancia_km(lat, lng, float(s["lat"]), float(s["lng"]))
        if dist_s <= 5.0:
            pontos_sigmine.append({
                "processo": s.get("processo"),
                "subs": s.get("subs"),
                "fase": s.get("fase"),
                "distancia_km": round(dist_s, 2),
                "lat": float(s["lat"]),
                "lng": float(s["lng"])
            })
            if "OURO" in s.get("subs", "").upper():
                score_ouro += 8
                evidencias_ouro.append(f"Processo {s['processo']} ({s['subs']}) a {dist_s:.1f} km")
            else:
                score_etr += 8
                evidencias_etr.append(f"Processo {s['processo']} ({s['subs']}) a {dist_s:.1f} km")
                
    pontos_sigmine = sorted(pontos_sigmine, key=lambda x: x["distancia_km"])[:20]
    
    score_final = min(100, max(score_ouro, score_etr))
    tipo_principal = "ouro" if score_ouro >= score_etr else "ETR"
    
    # Determina classificação
    if score_final >= 70:
        classificacao = "ALTO POTENCIAL"
    elif score_final >= 45:
        classificacao = "MEDIO POTENCIAL"
    elif score_final >= 20:
        classificacao = "BAIXO POTENCIAL"
    else:
        classificacao = "SEM INDICIOS"
        
    # Ponto de Interesse (Ponto Ideal)
    ponto_interesse = None
    if pontos_sigmine:
        ponto_interesse = {
            "lat": pontos_sigmine[0]["lat"],
            "lng": pontos_sigmine[0]["lng"],
            "score": score_final,
            "tipo": tipo_principal,
            "motivo": f"Foco em processo {pontos_sigmine[0]['processo']} de {pontos_sigmine[0]['subs']}"
        }
        
    # Camadas 3D do Subsolo
    camadas = [
        {"profundidade_cm": 0, "espessura_cm": 30, "tipo": "Solo Organico", "cor": "#8B7355"},
        {"profundidade_cm": 30, "espessura_cm": 40, "tipo": "Cascalho Aluvionar", "cor": "#A0522D"},
        {"profundidade_cm": 70, "espessura_cm": 50, "tipo": "Zona Mineralizada", "cor": "#FFD700" if tipo_principal == "ouro" else "#00FFFF"},
        {"profundidade_cm": 120, "espessura_cm": 80, "tipo": "Rocha Base", "cor": "#696969"}
    ]
    
    return {
        "score_final": score_final,
        "classificacao": classificacao,
        "tipo_principal": tipo_principal,
        "score_ouro": min(100, score_ouro),
        "score_etr": min(100, score_etr),
        "evidencias_ouro": evidencias_ouro[:5],
        "evidencias_etr": evidencias_etr[:5],
        "pontos_proximos": pontos_proximos,
        "pontos_sigmine": pontos_sigmine,
        "ponto_interesse": ponto_interesse,
        "camadas": camadas,
        "coordenada": {"lat": lat, "lng": lng}
    }
