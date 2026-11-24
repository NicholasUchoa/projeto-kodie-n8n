from enum import Enum

from pydantic import BaseModel, Field


class Categoria(str, Enum):
    duvida = "duvida"
    reclamacao = "reclamacao"
    solicitacao = "solicitacao"
    elogio = "elogio"
    outro = "outro"


class Setor(str, Enum):
    financeiro = "financeiro"
    suporte_tecnico = "suporte_tecnico"
    comercial = "comercial"
    atendimento_geral = "atendimento_geral"


class Prioridade(str, Enum):
    baixa = "baixa"
    media = "media"
    alta = "alta"


class Sentimento(str, Enum):
    positivo = "positivo"
    neutro = "neutro"
    negativo = "negativo"


class MensagemEntrada(BaseModel):
    mensagem: str = Field(min_length=3, max_length=5000, description="Texto enviado pelo cliente")
    remetente: str | None = Field(default=None, description="Nome ou e-mail do cliente")
    canal: str | None = Field(default=None, description="Origem: email, whatsapp, site...")


class ClassificacaoIA(BaseModel):
    """Campos que a IA precisa devolver (validados após a resposta)."""

    categoria: Categoria
    setor: Setor
    prioridade: Prioridade
    sentimento: Sentimento
    resumo: str = Field(min_length=1, max_length=300)
    confianca: float = Field(ge=0, le=1)
    resposta_sugerida: str = Field(min_length=1, max_length=1000)


class ClassificacaoSaida(ClassificacaoIA):
    """Resposta final da API: classificação + dados de contexto."""

    id: str
    mensagem_original: str
    remetente: str | None = None
    canal: str | None = None
    modelo: str
