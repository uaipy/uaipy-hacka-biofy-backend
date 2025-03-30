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
            {"role": "system", "content": "Você é um especialista em solos agrícolas."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5
    )
    return response.choices[0].message["content"]

# 4. Fluxo principal
def process_pdf(body, api_key) -> str:
    # URL do PDF
    url = body["document"].get("documentUrl", "")

    # Executa
    raw_text = extract_text_from_url(url)
    cleaned_text = clean_text(raw_text)

    # Crie um prompt técnico
    prompt = (
        "Analise o seguinte laudo de solo e forneça uma explicação técnica sobre a fertilidade, "
        "interpretação dos resultados e recomendações de correção caso necessário. Observação. Considere que sou pouco alfabetizado. Seja direto e use linguagem simples, que fascilitem a explicação. Evite elementos markdown. \n\n"
        f"{cleaned_text}"
    )

    # Envia para o GPT
    resposta = send_to_gpt(prompt, api_key)
    return resposta
