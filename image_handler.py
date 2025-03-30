

import base64
import os
import uuid

import openai
import requests


def process_image(body, api_key) -> str:
    url = body["image"].get("imageUrl", "")
    openai.api_key = api_key
    # Gera nome aleatório para o arquivo
    temp_image_path = f"{uuid.uuid4().hex}.jpeg"

    try:
        # Passo 1: Baixa a imagem e salva no disco
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception("Erro ao baixar a imagem")
        
        with open(temp_image_path, "wb") as f:
            f.write(response.content)

        # Passo 2: Lê e codifica a imagem em base64
        with open(temp_image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")

        # Passo 3: Envia a imagem para o GPT-4o
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Você é um agronomo inteligente e especialista em prevenção de pragas. Me descreva o que você vê nesta imagem, e caso encontre algum possivel problema, me ajude a solucionar."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1000
        )

        # Exibe a resposta
        return response['choices'][0]['message']['content']

    finally:
        # Passo 4: Remove a imagem temporária
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)
