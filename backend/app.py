"""API Flask - Olho de Deus (completa)"""
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from regras import calcular_score, calcular_simulacao_subsolo
from satelite import SateliteGIBS
from pdf_generator import gerar_pdf, gerar_memorial
import os
import io

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

@app.route('/api/simular-subsolo', methods=['POST'])
def simular_subsolo():
    dados = request.get_json()
    lat = float(dados.get('lat')); lng = float(dados.get('lng'))
    resultado = dados.get('resultado_analise')
    if not resultado:
        resultado = calcular_score(lat, lng)
    simulacao = calcular_simulacao_subsolo(resultado, lat, lng)
    return jsonify(simulacao)

@app.route('/api/gerar-pdf', methods=['POST'])
def gerar_pdf_endpoint():
    dados = request.get_json()
    caminho = '/tmp/relatorio_olho_deus.pdf'
    gerar_pdf(dados, caminho)
    return send_file(caminho, as_attachment=True, download_name='relatorio_olho_deus.pdf', mimetype='application/pdf')

@app.route('/api/gerar-memorial', methods=['POST'])
def gerar_memorial_endpoint():
    dados = request.get_json()
    caminho = '/tmp/memorial_descritivo.pdf'
    gerar_memorial(dados, caminho)
    return send_file(caminho, as_attachment=True, download_name='memorial_descritivo.pdf', mimetype='application/pdf')

@app.route('/api/exportar-kml', methods=['POST'])
def exportar_kml():
    dados = request.get_json()
    coord = dados.get("coordenada", {})
    pontos = dados.get("pontos_proximos", []) + dados.get("pontos_sigmine", [])
    kml = '<?xml version="1.0" encoding="UTF-8"?>\n<kml xmlns="http://www.opengis.net/kml/2.2">\n<Document>\n'
    kml += f'<name>Olho de Deus - {coord.get("lat")},{coord.get("lng")}</name>\n'
    kml += f'<Placemark><name>Ponto Analisado</name><Point><coordinates>{coord.get("lng")},{coord.get("lat")},0</coordinates></Point></Placemark>\n'
    for p in pontos:
        nome = p.get("nome") or p.get("processo", "Ponto")
        kml += f'<Placemark><name>{nome}</name><Point><coordinates>{p.get("lng")},{p.get("lat")},0</coordinates></Point></Placemark>\n'
    kml += '</Document>\n</kml>'
    return send_file(io.BytesIO(kml.encode("utf-8")), as_attachment=True, download_name='olho_de_deus.kml', mimetype='application/vnd.google-earth.kml+xml')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
