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
    
    pontos_proximos = []
    for r in REGIOES:
        dist = calcular_distancia_km(lat, lng, r["lat"], r["lng"])
        if dist <= 5.0:
            pontos_proximos.append({
                "nome": r["nome"], "tipo": r["tipo"], "distancia_km": round(dist, 2),
                "lat": r["lat"], "lng": r["lng"], "facilidade": r["facilidade"]
            })
            peso = 50 if dist < 1 else (30 if dist < 3 else 15)
            if r["tipo"] == "ouro":
                score_ouro += peso
                evidencias_ouro.append(f"Proximidade de {r['nome']} ({dist:.1f} km)")
            else:
                score_etr += peso
                evidencias_etr.append(f"Proximidade de {r['nome']} ({dist:.1f} km)")
                
    pontos_sigmine = []
    FOCO_MINERAL = ["OURO", "TERRAS RARAS", "ETR", "MONAZITA", "CASSITERITA", "ESTANHO", "SN", "TANTALITA", "NIOBIO"]
    
    for s in DADOS_SIGMINE:
        dist_s = calcular_distancia_km(lat, lng, float(s["lat"]), float(s["lng"]))
        if dist_s <= 5.0:
            subs = s.get("subs", "").upper()
            pontos_sigmine.append({
                "processo": s.get("processo"), "subs": s.get("subs"), "fase": s.get("fase"),
                "distancia_km": round(dist_s, 2), "lat": float(s["lat"]), "lng": float(s["lng"])
            })
            
            if any(foco in subs for foco in FOCO_MINERAL):
                if "OURO" in subs:
                    score_ouro += 8
                    evidencias_ouro.append(f"Processo {s['processo']} ({s['subs']}) a {dist_s:.1f} km")
                else:
                    score_etr += 8
                    evidencias_etr.append(f"Processo {s['processo']} ({s['subs']}) a {dist_s:.1f} km")
                
    pontos_sigmine = sorted(pontos_sigmine, key=lambda x: x["distancia_km"])
    pontos_foco = [p for p in pontos_sigmine if any(foco in p["subs"].upper() for foco in FOCO_MINERAL)]
    pontos_outros = [p for p in pontos_sigmine if p not in pontos_foco]
    pontos_sigmine = pontos_foco + pontos_outros
    
    score_final = min(100, max(score_ouro, score_etr))
    tipo_principal = "ouro" if score_ouro >= score_etr else "ETR"
    
    if score_final >= 70: classificacao = "ALTO POTENCIAL"
    elif score_final >= 45: classificacao = "MEDIO POTENCIAL"
    elif score_final >= 20: classificacao = "BAIXO POTENCIAL"
    else: classificacao = "SEM INDICIOS"
        
    ponto_interesse = None
    if pontos_foco:
        melhor = pontos_foco[0]
        tipo_pi = "ouro" if "OURO" in melhor["subs"].upper() else "ETR"
        ponto_interesse = {
            "lat": melhor["lat"], "lng": melhor["lng"], "score": score_final, "tipo": tipo_pi,
            "motivo": f"Foco em {melhor['subs']} (Processo {melhor['processo']})"
        }
        
    camadas = [
        {"profundidade_cm": 0, "espessura_cm": 30, "tipo": "Solo Organico", "cor": "#8B7355"},
        {"profundidade_cm": 30, "espessura_cm": 40, "tipo": "Cascalho Aluvionar", "cor": "#A0522D"},
        {"profundidade_cm": 70, "espessura_cm": 50, "tipo": "Zona Mineralizada", "cor": "#FFD700" if tipo_principal == "ouro" else "#00FFFF"},
        {"profundidade_cm": 120, "espessura_cm": 80, "tipo": "Rocha Base", "cor": "#696969"}
    ]
    
    return {
        "score_final": score_final, "classificacao": classificacao, "tipo_principal": tipo_principal,
        "score_ouro": min(100, score_ouro), "score_etr": min(100, score_etr),
        "evidencias_ouro": evidencias_ouro[:5], "evidencias_etr": evidencias_etr[:5],
        "pontos_proximos": pontos_proximos, "pontos_sigmine": pontos_sigmine[:20],
        "ponto_interesse": ponto_interesse, "camadas": camadas, "coordenada": {"lat": lat, "lng": lng}
    }
