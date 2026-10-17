from flask import Flask, send_from_directory
import os, sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')
sys.path.append(os.path.join(BASE_DIR, 'backend'))

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')

@app.route('/')
def index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

try:
    from backend.app import app as backend_app
    for rule in backend_app.url_map.iter_rules():
        if rule.endpoint != 'static' and rule.rule != '/':
            app.add_url_rule(rule.rule, rule.endpoint, backend_app.view_functions[rule.endpoint], methods=rule.methods)
except Exception as e:
    print("Aviso Backend:", e)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
