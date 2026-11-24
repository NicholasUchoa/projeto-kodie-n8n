import os

from google import genai
from google.genai import types
from pydantic import ValidationError

from .prompts import SCHEMA, SYSTEM_PROMPT, montar_mensagem_usuario
from .schemas import ClassificacaoIA

MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")


class ClassificacaoError(Exception):
    """Falha ao obter uma classificação válida da IA."""


class ConfiguracaoError(Exception):
    """Configuração ausente (ex.: chave de API)."""


def _get_client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ConfiguracaoError("Variável GEMINI_API_KEY não configurada.")
    return genai.Client(api_key=api_key)


def classificar(mensagem: str, remetente: str | None = None, canal: str | None = None) -> ClassificacaoIA:
    client = _get_client()
    resposta = client.models.generate_content(
        model=MODEL,
        contents=montar_mensagem_usuario(mensagem, remetente, canal),
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0,
            # Força a IA a responder SEMPRE em JSON no formato do schema.
            response_mime_type="application/json",
            response_json_schema=SCHEMA,
        ),
    )

    texto = resposta.text
    if not texto:
        raise ClassificacaoError("A IA não retornou conteúdo (possível bloqueio de segurança).")

    try:
        # Segunda camada de proteção: valida tipos, enums e limites.
        return ClassificacaoIA.model_validate_json(texto)
    except ValidationError as exc:
        raise ClassificacaoError(f"Resposta da IA fora do formato esperado: {exc}") from exc
