import os
import openai

# Configurar sua chave de API
openai.api_key = os.getenv("OPENAI_API_KEY")

# Lista de prompts
prompts = [
    "PROMPT 1: Explique a fotossíntese de forma simples.",
    "PROMPT 2: Quais são as principais culturas agrícolas do Brasil?",
    "PROMPT 3: Como funciona a previsão do tempo com IA?",
    "PROMPT 4: Resumo da Revolução Francesa em 3 parágrafos."
]

# Modelo a ser usado
model = "gpt-4o"

# Executar os prompts
for i, prompt in enumerate(prompts, 1):
    print(f"\nPrompt {i}: {prompt}")
    
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    
    reply = response.choices[0].message.content
    print(f"Resposta {i}:\n{reply}")
