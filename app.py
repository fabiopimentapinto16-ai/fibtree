from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from regras import calcular_score
from satelite import SateliteGIBS
from pdf_generator import gerar_pdf

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return jsonify({"status": "ok", "app": "Olho de Deus", "versao": "1.0"})

@app.route("/ping")
def ping():
    return "pong", 200

@app.route("/api/analisar", methods=["POST"])
def analisar():
    d = request.get_json()
    lat = float(d.get("lat")); lng = float(d.get("lng"))
    ds = None
    try:
        ds = SateliteGIBS().extrair_dados_espectrais(lat, lng)
    except Exception as e:
        print("Erro satelite: " + str(e))
    res = calcular_score(lat, lng, ds)
    if ds: res["dados_satelite"] = ds
    return jsonify(res)

@app.route("/api/gerar-pdf", methods=["POST"])
def gerar_pdf_endpoint():
    dados = request.get_json()
    caminho = "/tmp/relatorio_olho_deus.pdf"
    gerar_pdf(dados, caminho)
    return send_file(caminho, as_attachment=True, download_name="relatorio_olho_deus.pdf", mimetype="application/pdf")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
