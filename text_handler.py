import openai


def process_text(message, api_key) -> str:
    openai.api_key = api_key

    prompt_base = (
            "Você é um assistente agrícola especializado em ajudar produtores rurais "
            "a tomarem decisões com base em dados meteorológicos, solo, cultivo e produtividade. "
            "Forneça respostas claras, práticas e confiáveis. Use linguagem simples, direta e amigável. "
            "Se a pergunta for técnica, explique os conceitos de forma acessível."
            "\n\n"
            f"Pergunta do produtor: {message}\n"
            "Resposta:"
        )

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Você é um especialista em agricultura, controle de pragas e meteorologia que ajuda produtores rurais com orientações práticas."},
            {"role": "user", "content": prompt_base}
        ],
        temperature=0.7,
        max_tokens=800
    )

    return response['choices'][0]['message']['content']
