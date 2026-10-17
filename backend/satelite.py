
import requests
from io import BytesIO
from PIL import Image
import numpy as np
import math

class SateliteSentinel2:
    def __init__(self):
        self.base_url = "https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless-2023_3857/default/g/{z}/{y}/{x}.jpg"

    def _tile(self, lat, lng, zoom=14):
        lat_rad = math.radians(lat)
        n = 2.0 ** zoom
        x = int((lng + 180.0) / 360.0 * n)
        y = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
        return x, y

    def extrair_dados_espectrais(self, lat, lng):
        x, y = self._tile(lat, lng, 14)
        url = self.base_url.format(z=14, y=y, x=x)
        try:
            r = requests.get(url, timeout=15)
            r.raise_for_status()
            img = Image.open(BytesIO(r.content))
            arr = np.array(img.convert("RGB")).astype(float)
            r_v, g_v, b_v = arr[:,:,0], arr[:,:,1], arr[:,:,2]
            
            fe = np.clip(np.mean((r_v - b_v) / (r_v + b_v + 1e-6)) * 5, 0, 1)
            carb = np.clip(np.mean((g_v - r_v) / (g_v + r_v + 1e-6)) * 5, 0, 1)
            th = np.clip(np.mean(np.std(arr, axis=2)) / 255 * 3, 0, 1)

            return {
                "oxido_ferro": round(float(fe), 2),
                "carbonato_argila": round(float(carb), 2),
                "anomalia_radioativa": round(float(th), 2),
                "data_imagem": "2023-2024 (Sentinel-2)",
                "resolucao": "10m"
            }
        except Exception as e:
            print(f"[satelite] Falha no Sentinel-2: {e}")
            return None

class SateliteGIBS:
    BASE = "https://gibs.earthdata.nasa.gov/wmts/epsg3857/best"
    CAMADAS = {"modis_terra": "MODIS_Terra_CorrectedReflectance_TrueColor"}
    def __init__(self, camada="modis_terra"):
        self.camada = self.CAMADAS.get(camada, self.CAMADAS["modis_terra"])
    def _tile(self, lat, lng, zoom):
        lat_rad = math.radians(lat); n = 2.0 ** zoom
        return int((lng + 180.0) / 360.0 * n), int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    def buscar_imagem(self, lat, lng, data=None, zoom=8):
        from datetime import datetime, timedelta
        if data is None: data = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        x, y = self._tile(lat, lng, zoom)
        url = self.BASE + "/" + self.camada + "/default/" + data + "/GoogleMapsCompatible_Level9/" + str(zoom) + "/" + str(y) + "/" + str(x) + ".jpg"
        try:
            r = requests.get(url, timeout=15); r.raise_for_status()
            return Image.open(BytesIO(r.content))
        except: return None
    def extrair_dados_espectrais(self, lat, lng):
        img = self.buscar_imagem(lat, lng)
        if img is None: return None
        arr = np.array(img.convert("RGB"))
        r, g, b = arr[:,:,0].astype(float), arr[:,:,1].astype(float), arr[:,:,2].astype(float)
        total = r + g + b + 1
        rn, gn, bn = r/total, g/total, b/total
        fe = max(0, min(1, float(np.mean(rn - bn)) * 5))
        ca = max(0, min(1, float(np.mean(gn - rn * 0.5)) * 5))
        th = max(0, min(1, float(np.mean(np.std(arr, axis=2)) / 255) * 3))
        return {"oxido_ferro": round(fe, 2), "carbonato_argila": round(ca, 2), "anomalia_radioativa": round(th, 2), "data_imagem": "Ontem", "resolucao": "250m (MODIS)"}
