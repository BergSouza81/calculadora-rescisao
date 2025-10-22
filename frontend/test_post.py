import json
import urllib.request

url = "https://calculadora-rescisao.onrender.com/api/calcular"

payload = {
    "salario": 3000,
    "data_admissao": "2023-01-15",
    "data_demissao": "2023-10-10",
    "motivo": "pedido-demissao",
    "aviso_previo": "indenizado",
    "is_pcd": False,
    "horas_extras": [
        {"mes": 1, "quantidade": 10, "valor": 500},
        {"mes": 2, "quantidade": 15, "valor": 750}
    ]
}

data = json.dumps(payload).encode('utf-8')
req = urllib.request.Request(url, data=data, headers={
                             'Content-Type': 'application/json'})
try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        resp_text = resp.read().decode('utf-8')
        print(resp_text)
except Exception as e:
    print('ERROR:', e)
    raise
