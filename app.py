from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from calculo import CalculadoraTrabalhista
import os

# Serve frontend static files from the "frontend" folder
app = Flask(__name__, static_folder='frontend', static_url_path='')
CORS(app)


@app.route('/')
def home():
    # If the frontend index exists, serve it; otherwise return status JSON
    static_folder = app.static_folder or 'frontend'
    index_path = os.path.join(static_folder, 'index.html')
    if os.path.exists(index_path):
        return send_from_directory(static_folder, 'index.html')
    return jsonify({
        'status': 'online',
        'message': 'API Calculadora de Rescisão - Use o endpoint /api/calcular com método POST'
    })


@app.route('/api/calcular', methods=['POST'])
def calcular():
    dados = request.get_json()
    if not dados:
        return jsonify({
            'sucesso': False,
            'erro': 'Dados não fornecidos'
        }), 400

    resultado = CalculadoraTrabalhista.calcular_rescisao_completa(dados)
    return jsonify(resultado)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
