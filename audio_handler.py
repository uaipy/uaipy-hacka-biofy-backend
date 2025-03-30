import requests
import openai
from io import BytesIO



def process_audio(body, api_key) -> str:
    # Substitua pela sua chave da OpenAI
    openai.api_key = api_key

    # URL do arquivo de áudio
    audio_url =  body['audio'].get('audioUrl', "")

    # Passo 1: Baixar o áudio
    response = requests.get(audio_url)
    audio_bytes = BytesIO(response.content)
    audio_bytes.name = "audio.ogg"

    # Passo 2: Enviar para a API de transcrição da OpenAI (Whisper)
    transcription = openai.Audio.transcribe(
        model="whisper-1",
        file=audio_bytes,
        response_format="text"  # Pode ser json, srt, verbose_json, etc.
    )

    print("Transcrição do áudio:")
    print(transcription)
    
    prompt_base = (
        "Você é um assistente agrícola especializado em ajudar produtores rurais "
        "a tomarem decisões com base em dados meteorológicos, solo, cultivo e produtividade. "
        "Forneça respostas claras, práticas e confiáveis. Use linguagem simples, direta e amigável. "
        "Se a pergunta for técnica, explique os conceitos de forma acessível."
        "\n\n"
        f"Pergunta do produtor: {transcription}\n"
        "Resposta:"
    )

    # Passo 3 (opcional): Enviar a transcrição para o ChatGPT-4o
    chat_completion = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Você é um especialista em agricultura, controle de pragas e meteorologia que ajuda produtores rurais com orientações práticas."},
            {"role": "user", "content": prompt_base}
        ],
    )

    print("\nResposta do GPT-4o:")
    print(chat_completion.choices[0].message.content)
    return chat_completion.choices[0].message.content