from flask import Flask, send_from_directory
import os
app = Flask(__name__, static_folder='frontend', static_url_path='')
@app.route('/')
def index(): return send_from_directory('frontend', 'index.html')
try:
    import sys; sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
    from backend.app import app as backend_app
    app.wsgi_app = backend_app.wsgi_app
except Exception as e: print(e)
