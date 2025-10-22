from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from calculo import CalculadoraTrabalhista
import os

# Configuração do diretório de arquivos estáticos
STATIC_FOLDER = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'frontend')
app = Flask(__name__, static_folder=STATIC_FOLDER, static_url_path='')
CORS(app)


@app.route('/')
def home():
    try:
        return send_from_directory(STATIC_FOLDER, 'index.html')
    except Exception as e:
        app.logger.error(f"Erro ao servir index.html: {str(e)}")
        return jsonify({
            'status': 'erro',
            'mensagem': 'Erro ao carregar a página inicial. Por favor, tente novamente.'
        })


@app.route('/api/calcular', methods=['POST'])
def calcular():
    dados = request.get_json()
    if not dados:
        return jsonify({
            'sucesso': False,
            'erro': 'Dados não foram fornecidos. Por favor, preencha todos os campos obrigatórios.'
        }), 400

    resultado = CalculadoraTrabalhista.calcular_rescisao_completa(dados)
    return jsonify(resultado)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
