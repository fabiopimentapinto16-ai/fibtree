from flask import Flask, send_from_directory, jsonify, request, send_file
import os, sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')
sys.path.append(os.path.join(BASE_DIR, 'backend'))

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')

@app.route('/')
def index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

try:
    from regras import calcular_score
    BACKEND_OK = True
except Exception as e:
    print("Erro regras:", e)
    BACKEND_OK = False

@app.route('/api/analisar', methods=['POST'])
def analisar():
    d = request.get_json()
    if BACKEND_OK:
        try:
            return jsonify(calcular_score(float(d['lat']), float(d['lng'])))
        except Exception as e:
            return jsonify({"erro": str(e)}), 500
    return jsonify({"score_final": 50, "classificacao": "SIMULAÇÃO", "tipo_principal": "ouro"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
