from flask import Flask, request, jsonify
from flask_cors import CORS
from calculo import CalculadoraTrabalhista
import os

app = Flask(__name__)
CORS(app)


@app.route('/')
def home():
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
