from typing import Any, Dict

from pdf_handler import process_pdf


def montar_resposta(sender: str, phone: str, body: Dict[str, Any], api_key) -> Dict[str, str]:
    """Monta a resposta personalizada de acordo com o tipo de mensagem recebida."""
    mensagem_base = f"Olá {sender},"

    if isinstance(body.get("text"), dict):
        message = body["text"].get("message", "")
        return {
            "phone": phone,
            "message": f"{mensagem_base} recebi sua mensagem de TEXTO: \"{message}\". Essa é uma mensagem da UAIGRO para você se sentir mais confiante."
        }

    if isinstance(body.get("image"), dict):
        return {
            "phone": phone,
            "message": f"{mensagem_base} recebi sua IMAGEM. Essa é uma mensagem da UAIGRO para você se sentir mais confiante."
        }

    if isinstance(body.get("document"), dict):
        mime = body["document"].get("mimeType", "")
        if mime == "application/pdf":
            pdf_message = process_pdf(body, api_key)
            return {
                "phone": phone,
                "message": pdf_message
            }
        else:
            return {
                "phone": phone,
                "message": f"{mensagem_base} recebi seu documento, mas infelizmente só trabalhamos com PDF atualmente."
            }

    return {
        "phone": phone,
        "message": f"{mensagem_base} recebi sua mensagem. Mas infelizmente só trabalhamos com texto, imagens e PDFs."
    }