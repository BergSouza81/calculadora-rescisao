# Calculadora de Rescisão Trabalhista

API para cálculo de rescisão trabalhista desenvolvida em Python com Flask.

## Funcionalidades

- Cálculo de verbas rescisórias
- Suporte a diferentes tipos de rescisão
- Cálculo de férias proporcionais
- Cálculo de 13º salário
- Cálculo de FGTS
- Suporte a horas extras
- Cálculo especial para PCD

## Como usar

### Instalação

1. Clone o repositório
2. Instale as dependências:
```bash
pip install -r requirements.txt
```

### Executando localmente

```bash
python app.py
```

A API estará disponível em `http://localhost:5000`

### Endpoints

#### POST /api/calcular

Calcula a rescisão trabalhista com base nos dados fornecidos.

Exemplo de requisição:
```json
{
    "salario": 3000,
    "data_admissao": "2023-01-15",
    "data_demissao": "2023-10-10",
    "motivo": "pedido-demissao",
    "aviso_previo": "indenizado",
    "is_pcd": false,
    "horas_extras": [
        {"mes": 1, "quantidade": 10, "valor": 500},
        {"mes": 2, "quantidade": 15, "valor": 750},
        {"mes": 3, "quantidade": 5, "valor": 250}
    ]
}
```

Exemplo de resposta:
```json
{
    "sucesso": true,
    "verbas": {
        "saldo_salario": 1000.00,
        "ferias_proporcionais": 2916.67,
        "decimo_terceiro": 2500.00,
        "aviso_previo": 3000.00,
        "multa_fgts": 0.00,
        "media_horas_extras": 500.00,
        "total_geral": 9916.67
    },
    "detalhes": {
        "meses_trabalhados": 8,
        "dias_trabalhados_mes": 10
    }
}
```

## Desenvolvimento

O projeto usa:
- Python 3.14
- Flask para a API REST
- python-dateutil para cálculos de datas
- unittest para testes automatizados

### Executando os testes

```bash
python -m unittest tests/test_calculo.py -v
```

## Deploy

O projeto está configurado para deploy no Render.com usando gunicorn como servidor WSGI.