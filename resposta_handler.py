from typing import Any, Dict

from fastapi import HTTPException
import requests

from audio_handler import process_audio
from image_handler import process_image
from pdf_handler import process_pdf
from text_handler import process_text


def montar_resposta(sender: str, phone: str, body: Dict[str, Any], api_key, user, client_token, url) -> Dict[str, str]:
    """Monta a resposta personalizada de acordo com o tipo de mensagem recebida."""
    mensagem_base = f"Olá {sender},"

    if isinstance(body.get("text"), dict):
        message = process_text(body["text"].get("message", ""), api_key, user) 
        return {
            "phone": phone,
            "message": message
        }

    if isinstance(body.get("image"), dict):
        try:
            headers = {
                "Client-Token": client_token
            }
            user_response = {
                "phone": user.telefone,
                "message": "Estou dando uma olhada nessa imagem que você mandou, aguenta só um cadim."
            }
            response = requests.post(f"{url}/send-messages", json=user_response, headers=headers)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"[ERRO] Falha ao enviar mensagem para ZAPI: {e}")
            raise HTTPException(status_code=502, detail="Erro ao enviar mensagem para o provedor externo.")
        
        message = process_image(body, api_key, user)
        return {
            "phone": phone,
            "message": message
        }
    
    if isinstance(body.get("audio"), dict):
        try:
            headers = {
                "Client-Token": client_token
            }
            user_response = {
                "phone": user.telefone,
                "message": "To ouvindo seu áudio e já te respondo, ta?"
            }
            response = requests.post(f"{url}/send-messages", json=user_response, headers=headers)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"[ERRO] Falha ao enviar mensagem para ZAPI: {e}")
            raise HTTPException(status_code=502, detail="Erro ao enviar mensagem para o provedor externo.")
        
        message = process_audio(body, api_key, user)
        return {
            "phone": phone,
            "message": message
        }

    if isinstance(body.get("document"), dict):
        mime = body["document"].get("mimeType", "")
        if mime == "application/pdf":
            try:
                headers = {
                    "Client-Token": client_token
                }
                user_response = {
                    "phone": user.telefone,
                    "message": "Esse documento que você mandou ta cheio de informações interessantes, em?! Já to olhando tudinho aqui pra poder te ajudar."
                }
                response = requests.post(f"{url}/send-messages", json=user_response, headers=headers)
                response.raise_for_status()
            except requests.RequestException as e:
                print(f"[ERRO] Falha ao enviar mensagem para ZAPI: {e}")
                raise HTTPException(status_code=502, detail="Erro ao enviar mensagem para o provedor externo.")
            
            pdf_message = process_pdf(body, api_key, user)
            return {
                "phone": phone,
                "message": pdf_message
            }
        else:
            return {
                "phone": phone,
                "message": f"Eita, eu recebi o seu documento, mas por enquanto só trabalho com arquivos no formato PDF. Será que você poderia me enviar de novo no formato correto? Aí o negócio vai pra frente!"
            }

    return {
        "phone": phone,
        "message": f"{mensagem_base} tudo na paz? To vendo aqui que você me mandou algo, mas infelizmente só trabalho com textos, imagens, áudios e arquivos no formato PDF. Me mande outra mensagem, mas seguindo esses formatos, aí sim vou conseguir te ajudar!"
    }