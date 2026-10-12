"""Motor de Regras - Grãos de Ouro"""
import math
import json
import os
import time

# =========================================================
# PERFORMANCE: CACHE + ÍNDICE ESPACIAL (GRADE)
# =========================================================
_CACHE_ANALISES = {}
_CACHE_MAX = 500
_CACHE_TTL = 3600

def _chave_cache(lat, lng):
    return (round(lat, 3), round(lng, 3))

def _salvar_cache(lat, lng, resultado):
    _CACHE_ANALISES[_chave_cache(lat, lng)] = (resultado, time.time())
    if len(_CACHE_ANALISES) > _CACHE_MAX:
        mais_antigo = min(_CACHE_ANALISES, key=lambda k: _CACHE_ANALISES[k][1])
        del _CACHE_ANALISES[mais_antigo]

def _buscar_cache(lat, lng):
    entrada = _CACHE_ANALISES.get(_chave_cache(lat, lng))
    if entrada and (time.time() - entrada[1] < _CACHE_TTL):
        return entrada[0]
    return None

# === CARREGAMENTO DO SIGMINE ===
DADOS_SIGMINE = []
_caminho_json = os.path.join(os.path.dirname(__file__), "dados_sigmine.json")
if os.path.exists(_caminho_json):
    try:
        with open(_caminho_json, "r", encoding="utf-8") as _f:
            DADOS_SIGMINE = json.load(_f)
        print(f"[regras] Carregados {len(DADOS_SIGMINE)} registros do SIGMINE")
    except Exception as _e:
        print(f"[regras] Erro ao carregar SIGMINE: {_e}")

# === ÍNDICE ESPACIAL (GRADE) ===
_GRADE_ESPACIAL = {}
_TAMANHO_CELULA = 1.0

def _celula(lat, lng):
    return (int(lat // _TAMANHO_CELULA), int(lng // _TAMANHO_CELULA))

if DADOS_SIGMINE:
    for _reg in DADOS_SIGMINE:
        try:
            _lat = float(_reg["lat"]); _lng = float(_reg["lng"])
            _c = _celula(_lat, _lng)
            _GRADE_ESPACIAL.setdefault(_c, []).append(_reg)
        except Exception:
            pass
    print(f"[regras] Indice espacial: {len(_GRADE_ESPACIAL)} celulas")

def _candidatos_espacial(lat, lng, raio_celulas=1):
    lat_c, lng_c = _celula(lat, lng)
    resultado = []
    for d_lat in range(-raio_celulas, raio_celulas + 1):
        for d_lng in range(-raio_celulas, raio_celulas + 1):
            resultado.extend(_GRADE_ESPACIAL.get((lat_c + d_lat, lng_c + d_lng), []))
    return resultado

# =========================================================
# 39 REGIÕES CONHECIDAS (24 originais + 15 novas)
# =========================================================
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
    # === 15 NOVAS REGIÕES ===
    {"nome": "Vale do Ribeira", "lat": -24.5, "lng": -48.0, "raio": 1.0, "tipo": "ouro", "facilidade": "media"},
    {"nome": "Pilar de Goias", "lat": -14.5, "lng": -49.5, "raio": 0.8, "tipo": "ouro", "facilidade": "media"},
    {"nome": "Mara Rosa", "lat": -14.0, "lng": -49.2, "raio": 0.7, "tipo": "ouro", "facilidade": "media"},
    {"nome": "Ponte Branca", "lat": -16.5, "lng": -52.5, "raio": 0.8, "tipo": "ouro", "facilidade": "facil"},
    {"nome": "Roncador", "lat": -14.8, "lng": -50.3, "raio": 0.7, "tipo": "ouro", "facilidade": "facil"},
    {"nome": "Serra Leste", "lat": -6.2, "lng": -50.5, "raio": 0.6, "tipo": "ouro", "facilidade": "media"},
    {"nome": "Sossego", "lat": -6.4, "lng": -50.2, "raio": 0.5, "tipo": "ouro", "facilidade": "media"},
    {"nome": "Salobo", "lat": -5.8, "lng": -50.4, "raio": 0.6, "tipo": "ouro", "facilidade": "media"},
    {"nome": "Cristalino", "lat": -6.9, "lng": -50.6, "raio": 0.5, "tipo": "ouro", "facilidade": "media"},
    {"nome": "Andorinhas", "lat": -6.3, "lng": -50.3, "raio": 0.5, "tipo": "ouro", "facilidade": "media"},
    {"nome": "Tapira", "lat": -19.9, "lng": -46.8, "raio": 0.7, "tipo": "ETR", "facilidade": "media"},
    {"nome": "Serra do Salitre", "lat": -19.1, "lng": -46.6, "raio": 0.6, "tipo": "ETR", "facilidade": "dificil"},
    {"nome": "Patos de Minas", "lat": -18.6, "lng": -46.5, "raio": 0.8, "tipo": "ETR", "facilidade": "media"},
    {"nome": "Morro Azul", "lat": -21.5, "lng": -46.0, "raio": 0.6, "tipo": "ETR", "facilidade": "media"},
    {"nome": "Serra do Navio", "lat": 0.9, "lng": -52.0, "raio": 1.0, "tipo": "ETR", "facilidade": "media"},
]

def calcular_distancia_km(lat1, lng1, lat2, lng2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng/2)**2
    return R * 2 * math.asin(math.sqrt(a))

def calcular_score(lat, lng, dados_satelite=None):
    # VERIFICAR CACHE
    if dados_satelite is None:
        _cache_hit = _buscar_cache(lat, lng)
        if _cache_hit is not None:
            return _cache_hit

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
                evidencias_ouro.append(f"{r['nome']} a {dist_km:.1f} km (+{pontos} pts)")
            else:
                score_etr += pontos
                evidencias_etr.append(f"{r['nome']} a {dist_km:.1f} km (+{pontos} pts)")

            pontos_proximos.append({
                "nome": r["nome"], "tipo": r["tipo"],
                "distancia_km": round(dist_km, 1), "dentro": dentro,
                "facilidade": r["facilidade"], "lat": r["lat"], "lng": r["lng"]
            })

    if dados_satelite:
        fe = dados_satelite.get("oxido_ferro", 0)
        if fe > 0.7:
            score_ouro += 25
            evidencias_ouro.append(f"Alta anomalia de oxido de ferro ({fe:.2f}): +25 pts")
        elif fe > 0.4:
            score_ouro += 12
            evidencias_ouro.append(f"Anomalia moderada de oxido de ferro ({fe:.2f}): +12 pts")
        carb = dados_satelite.get("carbonato_argila", 0)
        if carb > 0.7:
            score_etr += 25
            evidencias_etr.append(f"Alta anomalia de carbonato/argila ({carb:.2f}): +25 pts")
        elif carb > 0.4:
            score_etr += 12
            evidencias_etr.append(f"Anomalia moderada de carbonato/argila ({carb:.2f}): +12 pts")
        th = dados_satelite.get("anomalia_radioativa", 0)
        if th > 0.6:
            score_etr += 20
            evidencias_etr.append(f"Anomalia radioativa detectada ({th:.2f}): +20 pts")

    # BUSCA NO SIGMINE (usando índice espacial)
    pontos_sigmine = []
    for s in _candidatos_espacial(lat, lng):
        try:
            dist_s = calcular_distancia_km(lat, lng, float(s["lat"]), float(s["lng"]))
            if dist_s <= 15:
                pontos_sigmine.append({
                    "nome": s.get("nome", ""), "subs": s.get("subs", ""),
                    "uf": s.get("uf", ""), "processo": s.get("processo", ""),
                    "fase": s.get("fase", ""), "distancia_km": round(dist_s, 2),
                    "lat": float(s["lat"]), "lng": float(s["lng"])
                })
                subs_upper = s.get("subs", "").upper()
                if "OURO" in subs_upper:
                    score_ouro += 10
                    evidencias_ouro.append(f"SIGMINE Ouro: Processo {s.get('processo')} (+10 pts)")
                elif any(x in subs_upper for x in ["TERRAS RARAS", "ETR", "LITIO", "NIOBIO"]):
                    score_etr += 10
                    evidencias_etr.append(f"SIGMINE Mineral Estrategico: Processo {s.get('processo')} (+10 pts)")
        except Exception:
            pass

    pontos_sigmine = sorted(pontos_sigmine, key=lambda x: x["distancia_km"])[:30]
    score_ouro = min(100, score_ouro)
    score_etr = min(100, score_etr)

    def classificar(s):
        if s >= 70: return "ALTO POTENCIAL"
        if s >= 45: return "MEDIO POTENCIAL"
        if s >= 20: return "BAIXO POTENCIAL"
        return "SEM INDICIOS"

    score_final = max(score_ouro, score_etr)
    tipo_principal = "ouro" if score_ouro >= score_etr else "ETR"

    resultado_final = {
        "score_final": score_final,
        "classificacao": classificar(score_final),
        "tipo_principal": tipo_principal,
        "score_ouro": score_ouro,
        "score_etr": score_etr,
        "evidencias_ouro": evidencias_ouro,
        "evidencias_etr": evidencias_etr,
        "pontos_proximos": sorted(pontos_proximos, key=lambda x: x["distancia_km"]),
        "pontos_sigmine": pontos_sigmine,
        "coordenada": {"lat": lat, "lng": lng},
        "raio_analisado_km": 15
    }
    _salvar_cache(lat, lng, resultado_final)
    return resultado_final

def calcular_simulacao_subsolo(resultado_analise, lat, lng):
    facilidade = "media"
    tipo_principal = resultado_analise.get("tipo_principal", "ouro")
    score = resultado_analise.get("score_final", 0)
    pontos = resultado_analise.get("pontos_proximos", [])
    if pontos:
        facilidade = pontos[0].get("facilidade", "media")

    camadas = []
    if facilidade == "facil":
        camadas = [
            {"profundidade_cm": 0, "espessura_cm": 30, "tipo": "Solo organico / areia fina", "cor": "#8B7355", "descricao": "Camada superficial com materia organica."},
            {"profundidade_cm": 30, "espessura_cm": 40, "tipo": "Areia grossa / cascalho", "cor": "#A0522D", "descricao": "Cascalho de fundo (stone line). Ouro tende a se concentrar."},
            {"profundidade_cm": 70, "espessura_cm": 50, "tipo": "Cascalho com argila", "cor": "#D2691E", "descricao": "Mistura de cascalho e argila."},
            {"profundidade_cm": 120, "espessura_cm": 80, "tipo": "Saprolito / rocha alterada", "cor": "#696969", "descricao": "Rocha mae ja intemperizada."},
        ]
    elif facilidade == "dificil":
        camadas = [
            {"profundidade_cm": 0, "espessura_cm": 20, "tipo": "Solo residual", "cor": "#8B7355", "descricao": "Camada fina de solo sobre rocha."},
            {"profundidade_cm": 20, "espessura_cm": 30, "tipo": "Saprolito", "cor": "#A0522D", "descricao": "Rocha parcialmente alterada."},
            {"profundidade_cm": 50, "espessura_cm": 150, "tipo": "Rocha macica", "cor": "#696969", "descricao": "Rocha sa. Ouro em veios de quartzo."},
        ]
    else:
        camadas = [
            {"profundidade_cm": 0, "espessura_cm": 25, "tipo": "Solo / areia", "cor": "#8B7355", "descricao": "Camada superficial mista."},
            {"profundidade_cm": 25, "espessura_cm": 55, "tipo": "Argila / cascalho", "cor": "#A0522D", "descricao": "Mistura de argila e cascalho."},
            {"profundidade_cm": 80, "espessura_cm": 70, "tipo": "Saprolito argiloso", "cor": "#D2691E", "descricao": "Zona de alteracao com argilas. Tipica de Terras Raras."},
            {"profundidade_cm": 150, "espessura_cm": 50, "tipo": "Rocha alterada", "cor": "#696969", "descricao": "Rocha mae intemperizada."},
        ]

    if tipo_principal == "ETR":
        for c in camadas:
            if "argila" in c["tipo"].lower() or "saprolito" in c["tipo"].lower():
                c["descricao"] += " Zona de adsorcao ionica de Terras Raras."

    prof_atual = 0
    if score > 0:
        espessura_dinamica = int((score / 100.0) * 80.0)
        espessura_dinamica = max(10, espessura_dinamica)
        if tipo_principal == "ouro":
            camada_mineral = {"profundidade_cm": 70, "espessura_cm": espessura_dinamica, "tipo": f"ZONA MINERALIZADA (OURO {score}%)", "cor": "#FFD700", "descricao": f"Camada mineralizada de Ouro proporcional ({espessura_dinamica}cm)."}
        else:
            camada_mineral = {"profundidade_cm": 80, "espessura_cm": espessura_dinamica, "tipo": f"ZONA MINERALIZADA (TERRAS RARAS {score}%)", "cor": "#00FFFF", "descricao": f"Camada mineralizada de Terras Raras proporcional ({espessura_dinamica}cm)."}
        camadas.append(camada_mineral)
        camadas.sort(key=lambda x: x["profundidade_cm"])
        for c in camadas:
            c["profundidade_cm"] = prof_atual
            prof_atual += c["espessura_cm"]

    return {
        "coordenada": {"lat": lat, "lng": lng},
        "tipo_terreno": facilidade,
        "tipo_principal": tipo_principal,
        "score": score,
        "camadas": camadas,
        "profundidade_total_cm": prof_atual if score > 0 else 200,
        "aviso": "SIMULACAO EDUCATIVA PROPORCIONAL. Baseada em perfis geologicos tipicos. NAO substitui GPR ou sondagem."
    }
