from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Substitua pelos dados da sua instância Z-API
INSTANCE_ID = 'sua-instancia-id'
TOKEN = 'seu-token'
ZAPI_URL = f'https://api.z-api.io/instances/{INSTANCE_ID}/token/{TOKEN}'

# Rota para enviar mensagens manualmente
@app.route('/enviar', methods=['POST'])
def enviar_mensagem():
    dados = request.json
    numero = dados.get('numero')  # Ex: "5591999999999"
    mensagem = dados.get('mensagem')

    payload = {
        "phone": numero,
        "message": mensagem
    }

    resposta = requests.post(f'{ZAPI_URL}/send-messages', json=payload)

    return jsonify(resposta.json()), resposta.status_code

# Webhook para receber mensagens
@app.route('/webhook/zapi', methods=['POST'])
def receber_mensagem():
    dados = request.json

    if dados.get("event") == "MESSAGE":
        mensagem = dados["message"]
        texto = mensagem.get("body")
        remetente = mensagem.get("from")
        nome = mensagem.get("name")

        print(f"📥 Nova mensagem de {nome} ({remetente}): {texto}")

        # Você pode responder automaticamente aqui se quiser
        resposta = {
            "phone": remetente,
            "message": f"Olá {nome}, recebi sua mensagem: \"{texto}\""
        }
        requests.post(f'{ZAPI_URL}/send-messages', json=resposta)

    return jsonify({"status": "recebido"}), 200

# Roda o servidor Flask
if __name__ == '__main__':
    app.run(port=5000)
