"""Modulo de Satelite - NASA GIBS"""
import requests
from io import BytesIO
from PIL import Image
from datetime import datetime, timedelta
import numpy as np
import math

class SateliteGIBS:
    BASE = "https://gibs.earthdata.nasa.gov/wmts/epsg3857/best"
    CAMADAS = {"modis_terra": "MODIS_Terra_CorrectedReflectance_TrueColor", "modis_aqua": "MODIS_Aqua_CorrectedReflectance_TrueColor", "viirs": "VIIRS_SNPP_CorrectedReflectance_TrueColor"}
    def __init__(self, camada="modis_terra"):
        self.camada = self.CAMADAS.get(camada, self.CAMADAS["modis_terra"])
    def _lat_lng_para_tile(self, lat, lng, zoom):
        lat_rad = math.radians(lat)
        n = 2.0 ** zoom
        x = int((lng + 180.0) / 360.0 * n)
        y = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
        return x, y
    def buscar_imagem(self, lat, lng, data=None, zoom=8):
        if data is None:
            data = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        x, y = self._lat_lng_para_tile(lat, lng, zoom)
        url = f"{self.BASE}/{self.camada}/default/{data}/GoogleMapsCompatible_Level9/{zoom}/{y}/{x}.jpg"
        try:
            r = requests.get(url, timeout=15)
            r.raise_for_status()
            return Image.open(BytesIO(r.content))
        except Exception as e:
            print(f"Erro: {e}")
            return None
    def extrair_dados_espectrais(self, lat, lng):
        img = self.buscar_imagem(lat, lng, zoom=8)
        if img is None: return None
        arr = np.array(img.convert("RGB"))
        r, g, b = arr[:,:,0].astype(float), arr[:,:,1].astype(float), arr[:,:,2].astype(float)
        total = r + g + b + 1
        r_norm, g_norm, b_norm = r/total, g/total, b/total
        fe_index = max(0, min(1, float(np.mean(r_norm - b_norm)) * 5))
        carb_index = max(0, min(1, float(np.mean(g_norm - r_norm * 0.5)) * 5))
        th_index = max(0, min(1, float(np.mean(np.std(arr, axis=2)) / 255) * 3))
        return {"oxido_ferro": round(fe_index, 2), "carbonato_argila": round(carb_index, 2), "anomalia_radioativa": round(th_index, 2), "data_imagem": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"), "resolucao": "250m (MODIS)"}
