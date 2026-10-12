"""Analise Espectral - Band Ratios"""
def calcular_band_ratios(bandas):
    b2 = bandas.get("b2", 1); b3 = bandas.get("b3", 1); b4 = bandas.get("b4", 1)
    b8 = bandas.get("b8", 1); b11 = bandas.get("b11", 1); b12 = bandas.get("b12", 1)
    oxido_ferro = b4 / b2 if b2 else 0
    argila = b11 / b12 if b12 else 0
    carbonato = b11 / b8 if b8 else 0
    gossan = (b4 + b3) / b2 if b2 else 0
    max_val = max(oxido_ferro, argila, carbonato, gossan, 1)
    return {"oxido_ferro": round(oxido_ferro/max_val, 2), "argila": round(argila/max_val, 2), "carbonato": round(carbonato/max_val, 2), "gossan": round(gossan/max_val, 2)}
def classificar_anomalia(valor):
    if valor > 0.7: return "ALTA"
    if valor > 0.4: return "MODERADA"
    if valor > 0.2: return "BAIXA"
    return "AUSENTE"
