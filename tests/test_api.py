from fastapi.testclient import TestClient

from app import classifier
from app.main import app
from app.schemas import ClassificacaoIA

client = TestClient(app)

FAKE = ClassificacaoIA(
    categoria="reclamacao",
    setor="financeiro",
    prioridade="alta",
    sentimento="negativo",
    resumo="Cliente cobrado duas vezes.",
    confianca=0.95,
    resposta_sugerida="Pedimos desculpas, vamos estornar o valor.",
)


def test_health():
    assert client.get("/health").status_code == 200


def test_classificar_ok(monkeypatch):
    monkeypatch.setattr(classifier, "classificar", lambda *a, **k: FAKE)
    r = client.post("/classificar", json={"mensagem": "Fui cobrado duas vezes!", "canal": "email"})
    assert r.status_code == 200
    body = r.json()
    assert body["setor"] == "financeiro"
    assert body["prioridade"] == "alta"
    assert body["mensagem_original"] == "Fui cobrado duas vezes!"
    assert "id" in body


def test_mensagem_vazia_rejeitada():
    assert client.post("/classificar", json={"mensagem": ""}).status_code == 422


def test_sem_chave_retorna_500(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    r = client.post("/classificar", json={"mensagem": "Olá, tenho uma dúvida"})
    assert r.status_code == 500
