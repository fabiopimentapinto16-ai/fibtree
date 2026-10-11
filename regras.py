import math

REGIOES = [
    {"nome": "Serra dos Carajas", "lat": -6.0, "lng": -50.0, "raio": 2.0, "tipo": "ouro", "facilidade": "media"},
    {"nome": "Cumaru", "lat": -6.5, "lng": -50.5, "raio": 1.0, "tipo": "ouro", "facilidade": "facil"},
    {"nome": "Serra Pelada", "lat": -5.9, "lng": -49.6, "raio": 0.8, "tipo": "ouro", "facilidade": "dificil"},
    {"nome": "Tucuma", "lat": -6.7, "lng": -51.2, "raio": 1.0, "tipo": "ouro", "facilidade": "facil"},
    {"nome": "Quadrilatero Ferrifero", "lat": -20.2, "lng": -43.8, "raio": 1.5, "tipo": "ouro", "facilidade": "dificil"},
    {"nome": "Morro do Pilar", "lat": -19.2, "lng": -43.4, "raio": 0.5, "tipo": "ouro", "facilidade": "dificil"},
    {"nome": "Jacobina", "lat": -11.2, "lng": -40.5, "raio": 1.0, "tipo": "ouro", "facilidade": "dificil"},
    {"nome": "Crixas", "lat": -14.5, "lng": -49.9, "raio": 1.0, "tipo": "ouro", "facilidade": "dificil"},
    {"nome": "Alta Floresta", "lat": -9.9, "lng": -56.1, "raio": 1.5, "tipo": "ouro", "facilidade": "facil"},
    {"nome": "Provincia Parima", "lat": 3.5, "lng": -63.0, "raio": 2.5, "tipo": "ouro", "facilidade": "facil"},
    {"nome": "Tepequem", "lat": 3.8, "lng": -61.7, "raio": 1.0, "tipo": "ouro", "facilidade": "facil"},
    {"nome": "Pacaraima", "lat": 4.5, "lng": -61.0, "raio": 1.0, "tipo": "ouro", "facilidade": "facil"},
    {"nome": "Uiramuta", "lat": 4.6, "lng": -60.2, "raio": 0.8, "tipo": "ouro", "facilidade": "facil"},
    {"nome": "Mundau", "lat": -4.5, "lng": -39.5, "raio": 0.8, "tipo": "ouro", "facilidade": "dificil"},
    {"nome": "Araxa", "lat": -19.6, "lng": -46.9, "raio": 0.8, "tipo": "ETR", "facilidade": "dificil"},
    {"nome": "Pocos de Caldas", "lat": -21.8, "lng": -46.5, "raio": 0.8, "tipo": "ETR", "facilidade": "media"},
    {"nome": "Minacu", "lat": -13.5, "lng": -48.2, "raio": 0.6, "tipo": "ETR", "facilidade": "media"},
    {"nome": "Complexo Barreira", "lat": 1.5, "lng": -61.0, "raio": 1.5, "tipo": "ETR", "facilidade": "media"},
    {"nome": "Morro dos Seis Lagos", "lat": 0.3, "lng": -66.5, "raio": 1.0, "tipo": "ETR", "facilidade": "dificil"},
    {"nome": "Cinturao Ribeira", "lat": -24.5, "lng": -47.5, "raio": 1.5, "tipo": "ETR", "facilidade": "media"},
    {"nome": "Barra do Itapirapua", "lat": -24.7, "lng": -48.5, "raio": 0.6, "tipo": "ETR", "facilidade": "dificil"},
    {"nome": "Catalao", "lat": -18.1, "lng": -47.9, "raio": 0.8, "tipo": "ETR", "facilidade": "dificil"},
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
    so, se = 0, 0
    eo, ee, pp = [], [], []
    for r in REGIOES:
        d = calcular_distancia_km(lat, lng, r["lat"], r["lng"])
        if d <= 15:
            if d < 1: p = 50; dentro = True
            elif d < 5: p = 25; dentro = False
            elif d < 10: p = 15; dentro = False
            else: p = 8; dentro = False
            if r["tipo"] == "ouro":
                so += p; eo.append(r["nome"] + " a " + str(round(d, 1)) + " km")
            else:
                se += p; ee.append(r["nome"] + " a " + str(round(d, 1)) + " km")
            pp.append({"nome": r["nome"], "tipo": r["tipo"], "distancia_km": round(d, 1), "dentro": dentro, "facilidade": r["facilidade"], "lat": r["lat"], "lng": r["lng"]})
    for x in pp:
        if x["facilidade"] == "facil":
            if x["tipo"] == "ouro": so += 15; eo.append("Terreno favoravel para detector (aluviao)")
            else: se += 10
    if dados_satelite:
        fe = dados_satelite.get("oxido_ferro", 0)
        if fe > 0.7: so += 25; eo.append("Alta anomalia de oxido de ferro")
        elif fe > 0.4: so += 12; eo.append("Anomalia moderada de oxido de ferro")
        ca = dados_satelite.get("carbonato_argila", 0)
        if ca > 0.7: se += 25; ee.append("Alta anomalia de carbonato/argila")
        elif ca > 0.4: se += 12; ee.append("Anomalia moderada de carbonato/argila")
        th = dados_satelite.get("anomalia_radioativa", 0)
        if th > 0.6: se += 20; ee.append("Anomalia radioativa detectada")
    so = min(100, so); se = min(100, se)
    def cl(s):
        if s >= 70: return "ALTO POTENCIAL"
        if s >= 45: return "MEDIO POTENCIAL"
        if s >= 20: return "BAIXO POTENCIAL"
        return "SEM INDICIOS"
    sf = max(so, se)
    tp = "ouro" if so >= se else "ETR"
    return {"score_final": sf, "classificacao": cl(sf), "tipo_principal": tp, "score_ouro": so, "score_etr": se, "evidencias_ouro": eo, "evidencias_etr": ee, "pontos_proximos": sorted(pp, key=lambda x: x["distancia_km"]), "coordenada": {"lat": lat, "lng": lng}, "raio_analisado_km": 15}
