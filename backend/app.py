import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
"""API Flask - Grãos de Ouro"""
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from regras import calcular_score, calcular_simulacao_subsolo
from satelite import SateliteGIBS
from pdf_generator import gerar_pdf, gerar_memorial
import os
import io

try:
    from flask_compress import Compress
    COMPRESS_DISPONIVEL = True
except ImportError:
    COMPRESS_DISPONIVEL = False

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

if COMPRESS_DISPONIVEL:
    Compress(app)
    print("[app] Compressao gzip ativada")

@app.route('/api/health')
def health():
    return jsonify({"status": "ok", "app": "Graos de Ouro"})

@app.route('/')
def index(): return send_from_directory('../frontend', 'index.html')

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
    caminho = '/tmp/relatorio_graos_de_ouro.pdf'
    gerar_pdf(dados, caminho)
    return send_file(caminho, as_attachment=True, download_name='relatorio_graos_de_ouro.pdf', mimetype='application/pdf')

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
    pontos_proximos = dados.get("pontos_proximos", [])
    pontos_sigmine = dados.get("pontos_sigmine", [])

    lat_central = coord.get("lat", 0)
    lng_central = coord.get("lng", 0)

    kml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    kml += '<kml xmlns="http://www.opengis.net/kml/2.2">\n'
    kml += '<Document>\n'
    kml += '<name>Graos de Ouro - Analise Mineral</name>\n'
    kml += f'<description>Ponto analisado: {lat_central:.6f}, {lng_central:.6f}</description>\n'

    # Estilos personalizados
    kml += '<Style id="pontoAnalisado">\n'
    kml += '<IconStyle><color>ff0000ff</color><scale>1.5</scale>'
    kml += '<Icon><href>http://maps.google.com/mapfiles/kml/paddle/blu-circle.png</href></Icon>'
    kml += '</IconStyle></Style>\n'

    kml += '<Style id="pontoOuro">\n'
    kml += '<IconStyle><color>ff00d7ff</color><scale>1.2</scale>'
    kml += '<Icon><href>http://maps.google.com/mapfiles/kml/paddle/ylw-circle.png</href></Icon>'
    kml += '</IconStyle></Style>\n'

    kml += '<Style id="pontoETR">\n'
    kml += '<IconStyle><color>ffffd700</color><scale>1.2</scale>'
    kml += '<Icon><href>http://maps.google.com/mapfiles/kml/paddle/wht-circle.png</href></Icon>'
    kml += '</IconStyle></Style>\n'

    kml += '<Style id="pontoSigmine">\n'
    kml += '<IconStyle><color>ff00ff00</color><scale>1.0</scale>'
    kml += '<Icon><href>http://maps.google.com/mapfiles/kml/paddle/grn-circle.png</href></Icon>'
    kml += '</IconStyle></Style>\n'

    # Ponto analisado
    kml += '<Placemark>\n'
    kml += '<name>PONTO ANALISADO</name>\n'
    kml += f'<description><![CDATA[<b>Coordenada:</b> {lat_central:.6f}, {lng_central:.6f}<br/><b>Score:</b> {dados.get("score_final", 0)}/100<br/><b>Classificacao:</b> {dados.get("classificacao", "")}<br/><b>Tipo:</b> {dados.get("tipo_principal", "").upper()}]]></description>\n'
    kml += '<styleUrl>#pontoAnalisado</styleUrl>\n'
    kml += f'<Point><coordinates>{lng_central},{lat_central},0</coordinates></Point>\n'
    kml += '</Placemark>\n'

    # Regiões conhecidas
    for p in pontos_proximos:
        tipo = p.get("tipo", "ouro")
        estilo = "#pontoOuro" if tipo == "ouro" else "#pontoETR"
        cor_nome = "OURO" if tipo == "ouro" else "TERRAS RARAS"
        kml += '<Placemark>\n'
        kml += f'<name>{p.get("nome", "")} ({cor_nome})</name>\n'
        kml += f'<description><![CDATA[<b>Regiao conhecida:</b> {p.get("nome", "")}<br/><b>Tipo:</b> {cor_nome}<br/><b>Distancia:</b> {p.get("distancia_km", 0)} km<br/><b>Facilidade:</b> {p.get("facilidade", "")}]]></description>\n'
        kml += f'<styleUrl>{estilo}</styleUrl>\n'
        kml += f'<Point><coordinates>{p.get("lng", 0)},{p.get("lat", 0)},0</coordinates></Point>\n'
        kml += '</Placemark>\n'

    # Processos SIGMINE
    for s in pontos_sigmine:
        subs = s.get("subs", "Nao informada")
        fase = s.get("fase", "Nao informada")
        kml += '<Placemark>\n'
        kml += f'<name>Processo {s.get("processo", "")} - {subs}</name>\n'
        kml += f'<description><![CDATA[<b>Processo:</b> {s.get("processo", "")}<br/><b>Substancia:</b> {subs}<br/><b>Fase:</b> {fase}<br/><b>Distancia:</b> {s.get("distancia_km", 0)} km<br/><b>UF:</b> {s.get("uf", "")}]]></description>\n'
        kml += '<styleUrl>#pontoSigmine</styleUrl>\n'
        kml += f'<Point><coordinates>{s.get("lng", 0)},{s.get("lat", 0)},0</coordinates></Point>\n'
        kml += '</Placemark>\n'

    kml += '</Document>\n'
    kml += '</kml>'

    return send_file(io.BytesIO(kml.encode("utf-8")), as_attachment=True, download_name='graos_de_ouro.kml', mimetype='application/vnd.google-earth.kml+xml')

