from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from calculo import CalculadoraTrabalhista
import os

# Configuração do diretório de arquivos estáticos
app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app)


@app.route('/')
def home():
    try:
        return send_from_directory('static', 'index.html')
    except Exception as e:
        app.logger.error(f"Erro ao servir index.html: {str(e)}")
        return jsonify({
            'status': 'erro',
            'mensagem': 'Erro ao carregar a página inicial. Por favor, tente novamente.'
        })


@app.route('/api/calcular_rescisao', methods=['POST'])
def calcular_rescisao():
    dados = request.get_json()
    if not dados:
        return jsonify({
            'sucesso': False,
            'erro': 'Dados não foram fornecidos. Por favor, preencha todos os campos obrigatórios.'
        }), 400

    try:
        resultado = CalculadoraTrabalhista.calcular_rescisao_completa(dados)
        return jsonify({
            'sucesso': True,
            'saldo_salario': resultado.get('saldo_salario', 0),
            'aviso_previo': resultado.get('aviso_previo', 0),
            'ferias_proporcionais': resultado.get('ferias_proporcionais', 0),
            'ferias_vencidas': resultado.get('ferias_vencidas', 0),
            'decimo_terceiro': resultado.get('decimo_terceiro', 0),
            'multa_fgts': resultado.get('multa_fgts', 0),
            'total_descontos': resultado.get('total_descontos', 0),
            'total_liquido': resultado.get('total_liquido', 0)
        })
    except Exception as e:
        app.logger.error(f"Erro ao calcular rescisão: {str(e)}")
        return jsonify({
            'sucesso': False,
            'erro': 'Erro ao calcular rescisão. Por favor, verifique os dados e tente novamente.'
        }), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
