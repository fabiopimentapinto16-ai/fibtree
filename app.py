from flask import Flask, send_from_directory, jsonify, request, send_file
from flask_cors import CORS
import os, sys

app = Flask(__name__, static_folder='frontend', static_url_path='')
CORS(app)

@app.route('/')
def index(): return send_from_directory('frontend', 'index.html')

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
try:
    from backend.regras import calcular_score
    from backend.pdf_generator import gerar_pdf
    BACKEND_OK = True
except Exception as e:
    print("Erro ao conectar backend:", e)
    BACKEND_OK = False

@app.route('/api/analisar', methods=['POST'])
def analisar():
    d = request.get_json()
    if BACKEND_OK: return jsonify(calcular_score(float(d['lat']), float(d['lng'])))
    return jsonify({"score_final": 50, "classificacao": "SIMULAÇÃO", "tipo_principal": "ouro"})

@app.route('/api/gerar-pdf', methods=['POST'])
def route_pdf():
    if BACKEND_OK:
        c = "/tmp/rel.pdf"; gerar_pdf(request.get_json(), c)
        return send_file(c, as_attachment=True, download_name='relatorio.pdf')
    return jsonify({"erro": "Falhou"}), 500

if __name__ == '__main__': app.run(host='0.0.0.0', port=5000)
