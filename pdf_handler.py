import tempfile
import fitz  # PyMuPDF
import re
import openai
import requests

# 1. Extrair o texto do PDF
def extract_text_from_url(url):
    response = requests.get(url)
    response.raise_for_status()

    # Cria um arquivo temporário e já o abre para leitura com PyMuPDF
    with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp:
        tmp.write(response.content)
        tmp.flush()  # garante que os dados estão salvos em disco

        # Abre o PDF com o caminho do arquivo temporário
        doc = fitz.open(tmp.name)
        full_text = ""
        for page in doc:
            full_text += page.get_text()

    # O arquivo temporário é deletado automaticamente ao sair do `with`
    return full_text

# 2. Limpar o texto e preparar a entrada
def clean_text(text):
    # Remove múltiplos espaços e linhas em branco
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()

# 3. Enviar para a OpenAI (ajuste seu modelo e chave API)
def send_to_gpt(prompt, api_key, model="gpt-4o"):
    openai.api_key = api_key

    
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "Você é um especialista em agricultura, controle de pragas e meteorologia que ajuda produtores rurais com orientações práticas."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5
    )
    return response.choices[0].message["content"]

# 4. Fluxo principal
def process_pdf(body, api_key, user) -> str:
    # URL do PDF
    url = body["document"].get("documentUrl", "")

    # Executa
    raw_text = extract_text_from_url(url)
    cleaned_text = clean_text(raw_text)

    prompt_base = (
            "Você é um assistente agrícola especializado em ajudar produtores rurais "
            "a tomarem decisões com base em dados meteorológicos, solo, cultivo e produtividade. "
            "Forneça respostas claras, práticas e confiáveis. Use linguagem simples, direta e amigável. "
            "Se a pergunta for técnica, explique os conceitos de forma acessível."
            "\n\n"
            "Esses são os dados do produtor a serem utilizados como contexto:"
            f"Dados do produtor: {user.details}\n"
            "\n\n"
            f"Analise o seguinte laudo de solo e forneça uma explicação técnica sobre a fertilidade.\n"
            "\n\n"
            f"Dados do laudo: {cleaned_text}\n"
            "\n\n"
            "Resposta:"
        )

    # Envia para o GPT
    resposta = send_to_gpt(prompt_base, api_key)
    return resposta
