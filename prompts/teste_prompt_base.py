import os
import openai

# Configurar sua chave de API
openai.api_key = "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" #ADD THE KEY HERE - DO NOT COMMIT SECRETS

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
