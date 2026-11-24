import logging
import uuid

from google.genai import errors as genai_errors
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

load_dotenv()

from . import classifier  # noqa: E402
from .schemas import ClassificacaoSaida, MensagemEntrada  # noqa: E402

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("classificador")

app = FastAPI(
    title="Classificador de Mensagens com IA",
    description="Recebe mensagens de clientes, classifica com IA e devolve JSON para o fluxo n8n.",
    version="1.0.0",
)


@app.get("/health", tags=["infra"])
def health():
    return {"status": "ok", "modelo": classifier.MODEL}


@app.post("/classificar", response_model=ClassificacaoSaida, tags=["classificação"])
def classificar(entrada: MensagemEntrada):
    try:
        resultado = classifier.classificar(entrada.mensagem, entrada.remetente, entrada.canal)
    except classifier.ConfiguracaoError as exc:
        log.error("Configuração inválida: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except classifier.ClassificacaoError as exc:
        log.error("Resposta inválida da IA: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except genai_errors.APIError as exc:
        log.error("Erro na API de IA: %s", exc)
        raise HTTPException(status_code=502, detail="Falha ao consultar o provedor de IA.") from exc

    saida = ClassificacaoSaida(
        id=str(uuid.uuid4()),
        mensagem_original=entrada.mensagem,
        remetente=entrada.remetente,
        canal=entrada.canal,
        modelo=classifier.MODEL,
        **resultado.model_dump(),
    )
    log.info("Mensagem %s -> %s/%s/%s", saida.id, saida.categoria.value, saida.setor.value, saida.prioridade.value)
    return saida
