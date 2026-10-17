import re
from flask import Blueprint
bp_anti = Blueprint("anti_bitola", __name__)
_PAT = re.compile(r'<img[^>]*(?:src|alt)\s*=\s*["\'][^"\']*(?:avatar|perfil|user|analista|homem|man|person|unsplash|pexels)[^"\']*["\'][^>]*>', re.I)
@bp_anti.after_app_request
def _aplicar(resp):
    try:
        if "text/html" in resp.headers.get("Content-Type", "") and not resp.is_streamed:
            body = resp.get_data(as_text=True)
            resp.set_data(_PAT.sub("", body))
    except: pass
    return resp
