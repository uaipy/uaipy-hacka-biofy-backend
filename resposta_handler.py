from typing import Any, Dict

from audio_handler import process_audio
from image_handler import process_image
from pdf_handler import process_pdf
from text_handler import process_text


def montar_resposta(sender: str, phone: str, body: Dict[str, Any], api_key, user) -> Dict[str, str]:
    """Monta a resposta personalizada de acordo com o tipo de mensagem recebida."""
    mensagem_base = f"Olá {sender},"

    if isinstance(body.get("text"), dict):
        message = process_text(body["text"].get("message", ""), api_key, user) 
        return {
            "phone": phone,
            "message": message
        }

    if isinstance(body.get("image"), dict):
        message = process_image(body, api_key, user)
        return {
            "phone": phone,
            "message": message
        }
    
    if isinstance(body.get("audio"), dict):
        message = process_audio(body, api_key, user)
        return {
            "phone": phone,
            "message": message
        }

    if isinstance(body.get("document"), dict):
        mime = body["document"].get("mimeType", "")
        if mime == "application/pdf":
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