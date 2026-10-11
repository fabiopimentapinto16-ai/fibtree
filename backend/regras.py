"""Motor de Regras - Olho de Deus (Ouro + Terras Raras)"""
import math

REGIOES = [
    {"nome": "Serra dos Carajás", "lat": -6.0, "lng": -50.0, "raio": 2.0, "tipo": "ouro", "facilidade": "media"},
    {"nome": "Cumaru", "lat": -6.5, "lng": -50.5, "raio": 1.0, "tipo": "ouro", "facilidade": "facil"},
    {"nome": "Serra Pelada", "lat": -5.9, "lng": -49.6, "raio": 0.8, "tipo": "ouro", "facilidade": "dificil"},
    {"nome": "Tucumã", "lat": -6.7, "lng": -51.2, "raio": 1.0, "tipo": "ouro", "facilidade": "facil"},
    {"nome": "Quadrilátero Ferrífero", "lat": -20.2, "lng": -43.8, "raio": 1.5, "tipo": "ouro", "facilidade": "dificil"},
    {"nome": "Morro do Pilar", "lat": -19.2, "lng": -43.4, "raio": 0.5, "tipo": "ouro", "facilidade": "dificil"},
    {"nome": "Jacobina", "lat": -11.2, "lng": -40.5, "raio": 1.0, "tipo": "ouro", "facilidade": "dificil"},
    {"nome": "Crixás", "lat": -14.5, "lng": -49.9, "raio": 1.0, "tipo": "ouro", "facilidade": "dificil"},
    {"nome": "Alta Floresta", "lat": -9.9, "lng": -56.1, "raio": 1.5, "tipo": "ouro", "facilidade": "facil"},
    {"nome": "Província Parima", "lat": 3.5, "lng": -63.0, "raio": 2.5, "tipo": "ouro", "facilidade": "facil"},
    {"nome": "Tepequém", "lat": 3.8, "lng": -61.7, "raio": 1.0, "tipo": "ouro", "facilidade": "facil"},
    {"nome": "Pacaraima", "lat": 4.5, "lng": -61.0, "raio": 1.0, "tipo": "ouro", "facilidade": "facil"},
    {"nome": "Uiramutã", "lat": 4.6, "lng": -60.2, "raio": 0.8, "tipo": "ouro", "facilidade": "facil"},
    {"nome": "Mundau", "lat": -4.5, "lng": -39.5, "raio": 0.8, "tipo": "ouro", "facilidade": "dificil"},
    {"nome": "Araxá", "lat": -19.6, "lng": -46.9, "raio": 0.8, "tipo": "ETR", "facilidade": "dificil"},
    {"nome": "Poços de Caldas", "lat": -21.8, "lng": -46.5, "raio": 0.8, "tipo": "ETR", "facilidade": "media"},
    {"nome": "Minaçu", "lat": -13.5, "lng": -48.2, "raio": 0.6, "tipo": "ETR", "facilidade": "media"},
    {"nome": "Complexo Barreira", "lat": 1.5, "lng": -61.0, "raio": 1.5, "tipo": "ETR", "facilidade": "media"},
    {"nome": "Morro dos Seis Lagos", "lat": 0.3, "lng": -66.5, "raio": 1.0, "tipo": "ETR", "facilidade": "dificil"},
    {"nome": "Cinturão Ribeira", "lat": -24.5, "lng": -47.5, "raio": 1.5, "tipo": "ETR", "facilidade": "media"},
    {"nome": "Barra do Itapirapuã", "lat": -24.7, "lng": -48.5, "raio": 0.6, "tipo": "ETR", "facilidade": "dificil"},
    {"nome": "Catalão", "lat": -18.1, "lng": -47.9, "raio": 0.8, "tipo": "ETR", "facilidade": "dificil"},
    {"nome": "Salitre", "lat": -19.0, "lng": -46.8, "raio": 0.5, "tipo": "ETR", "facilidade": "media"},
    {"nome": "Serra Negra", "lat": -8.1, "lng": -38.0, "raio": 0.8, "tipo": "ETR", "facilidade": "dificil"},
]

def calcular_distancia_km(lat1, lng1, lat2, lng2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng/2)**2
    return R * 2 * math.asin(math.sqrt(a))

def calcular_score(lat, lng, dados_satelite=None):
    score_ouro = 0
    score_etr = 0
    evidencias_ouro = []
    evidencias_etr = []
    pontos_proximos = []
    
    for r in REGIOES:
        dist_km = calcular_distancia_km(lat, lng, r["lat"], r["lng"])
        if dist_km <= 15:
            if dist_km < 1: pontos = 50; dentro = True
            elif dist_km < 5: pontos = 25; dentro = False
            elif dist_km < 10: pontos = 15; dentro = False
            else: pontos = 8; dentro = False
            
            if r["tipo"] == "ouro":
                score_ouro += pontos
                evidencias_ouro.append(f"{r['nome']} a {dist_km:.1f} km")
            else:
                score_etr += pontos
                evidencias_etr.append(f"{r['nome']} a {dist_km:.1f} km")
            
            pontos_proximos.append({
                "nome": r["nome"], "tipo": r["tipo"],
                "distancia_km": round(dist_km, 1), "dentro": dentro,
                "facilidade": r["facilidade"], "lat": r["lat"], "lng": r["lng"]
            })
    
    for p in pontos_proximos:
        if p["facilidade"] == "facil":
            if p["tipo"] == "ouro": score_ouro += 15; evidencias_ouro.append("Terreno favorável para detector (aluvião)")
            else: score_etr += 10; evidencias_etr.append("Terreno favorável para ETR")
    
    if dados_satelite:
        fe = dados_satelite.get("oxido_ferro", 0)
        if fe > 0.7: score_ouro += 25; evidencias_ouro.append(f"Alta anomalia de óxido de ferro ({fe:.2f})")
        elif fe > 0.4: score_ouro += 12; evidencias_ouro.append(f"Anomalia moderada de óxido de ferro ({fe:.2f})")
        
        carb = dados_satelite.get("carbonato_argila", 0)
        if carb > 0.7: score_etr += 25; evidencias_etr.append(f"Alta anomalia de carbonato/argila ({carb:.2f})")
        elif carb > 0.4: score_etr += 12; evidencias_etr.append(f"Anomalia moderada de carbonato/argila ({carb:.2f})")
        
        th = dados_satelite.get("anomalia_radioativa", 0)
        if th > 0.6: score_etr += 20; evidencias_etr.append(f"Anomalia radioativa detectada ({th:.2f})")
    
    score_ouro = min(100, score_ouro)
    score_etr = min(100, score_etr)
    
    def classificar(s):
        if s >= 70: return "ALTO POTENCIAL"
        if s >= 45: return "MÉDIO POTENCIAL"
        if s >= 20: return "BAIXO POTENCIAL"
        return "SEM INDÍCIOS"
    
    score_final = max(score_ouro, score_etr)
    tipo_principal = "ouro" if score_ouro >= score_etr else "ETR"
    
    return {
        "score_final": score_final,
        "classificacao": classificar(score_final),
        "tipo_principal": tipo_principal,
        "score_ouro": score_ouro,
        "score_etr": score_etr,
        "evidencias_ouro": evidencias_ouro,
        "evidencias_etr": evidencias_etr,
        "pontos_proximos": sorted(pontos_proximos, key=lambda x: x["distancia_km"]),
        "coordenada": {"lat": lat, "lng": lng},
        "raio_analisado_km": 15
    }
