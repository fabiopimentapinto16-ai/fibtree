"""API Flask - Olho de Deus"""
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from regras import calcular_score
from satelite import SateliteGIBS
from pdf_generator import gerar_pdf
import os

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

@app.route('/')
def index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/api/analisar', methods=['POST'])
def analisar():
    dados = request.get_json()
    lat = float(dados.get('lat')); lng = float(dados.get('lng'))
    usar_satelite = dados.get('usar_satelite', True)
    dados_sat = None
    if usar_satelite:
        try:
            sat = SateliteGIBS()
            dados_sat = sat.extrair_dados_espectrais(lat, lng)
        except Exception as e:
            print(f"Erro satelite: {e}")
    resultado = calcular_score(lat, lng, dados_sat)
    if dados_sat: resultado["dados_satelite"] = dados_sat
    return jsonify(resultado)

@app.route('/api/gerar-pdf', methods=['POST'])
def gerar_pdf_endpoint():
    dados = request.get_json()
    caminho = '/tmp/relatorio_olho_deus.pdf'
    gerar_pdf(dados, caminho)
    return send_file(caminho, as_attachment=True, download_name='relatorio_olho_deus.pdf', mimetype='application/pdf')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
