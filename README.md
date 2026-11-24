# 📨 Classificador de Mensagens com IA + n8n

Solução que **classifica automaticamente mensagens de clientes** usando Inteligência Artificial e **encaminha cada uma ao setor responsável** por meio de um fluxo de automação no n8n.

> Projeto do Desafio Técnico KODIE — IA e Automação · Caso 4.1 (Classificação de Mensagens)

---

## 1. Apresentação da Ideia

<!-- ✏️ PERSONALIZE este trecho com a sua história. Exemplo abaixo. -->
A ideia surgiu de uma situação comum em pequenas empresas: o atendimento recebe dezenas de mensagens por dia (e-mail, WhatsApp, site) e alguém precisa ler uma a uma e decidir para quem encaminhar. Isso é lento, sujeito a erros e faz mensagens urgentes se perderem no meio das demais. Quis mostrar que a IA pode assumir essa triagem inicial e que a automação pode fazer o envio ao setor certo, deixando as pessoas livres para o que realmente exige atenção humana.

## 2. Problema Escolhido

**Caso 4.1 — Classificação de Mensagens.** Uma empresa recebe mensagens de clientes (dúvidas, reclamações, solicitações) sem processo organizado de triagem. O encaminhamento manual consome tempo e dificulta a organização dos atendimentos.

## 3. Solução Proposta

1. O cliente (ou outro sistema) envia a mensagem para um **webhook do n8n**.
2. O n8n normaliza os dados e chama a **API FastAPI** (`POST /classificar`).
3. A API envia a mensagem a um **modelo de IA (Google Gemini)** com um prompt estruturado.
4. A IA devolve um **JSON** com categoria, setor, prioridade, sentimento, resumo, confiança e uma resposta sugerida.
5. O n8n usa o campo `setor` para **rotear** a mensagem à fila/e-mail do setor correto e devolve o resultado.

**Qual o papel da IA?** Ela *interpreta* o texto livre (algo que regras fixas fazem mal), *decide* categoria, setor e urgência, e *redige* um rascunho de resposta. A automação apenas executa o que a IA decidiu.

### Exemplo de resposta da API

```json
{
  "categoria": "reclamacao",
  "setor": "financeiro",
  "prioridade": "alta",
  "sentimento": "negativo",
  "resumo": "Cliente foi cobrado duas vezes no cartão e exige estorno urgente.",
  "confianca": 0.96,
  "resposta_sugerida": "Olá! Pedimos desculpas pelo transtorno. Já encaminhamos ao financeiro para análise e estorno.",
  "id": "b0c1...",
  "mensagem_original": "Fui cobrado duas vezes no cartão...",
  "remetente": "maria@email.com",
  "canal": "email",
  "modelo": "gemini-3.8-flash"
}
```

### Como garantimos o formato correto da resposta da IA

- **Saída estruturada:** a chamada usa `response_mime_type=application/json` com um JSON Schema com `enum`s — a IA só consegue responder no formato definido.
- **Validação dupla:** a resposta ainda passa pelo **Pydantic**; se algo vier fora do padrão, a API devolve erro `502` em vez de propagar dado ruim.
- **Temperatura 0** para respostas consistentes.
- **Proteção contra prompt injection:** a mensagem do cliente vai delimitada em `<mensagem_cliente>` e o prompt instrui a tratá-la apenas como dado.

## 4. Tecnologias Utilizadas

| Camada | Tecnologia |
|---|---|
| IA | API do Google Gemini (`google-genai`) |
| Back-end | Python 3.12 + **FastAPI** + Pydantic |
| Automação | **n8n** |
| Infra (opcional) | Docker + Docker Compose |
| Testes | pytest |

## 5. Funcionamento do Sistema

```
Cliente ──► [Webhook n8n] ──► [Edit Fields] ──► [HTTP Request] ──► API FastAPI ──► Gemini
                                                      │                              │
                                                      ◄────────── JSON ◄─────────────┘
                                                      ▼
                                              [Switch por setor]
                                 ┌───────────┬───────┴─────┬──────────────┐
                            Financeiro   Suporte      Comercial   Atendimento Geral
                                 └───────────┴───────┬─────┴──────────────┘
                                              [Respond to Webhook]
```

**API (`app/`)**
- `main.py` — endpoints `GET /health` e `POST /classificar`, tratamento de erros.
- `schemas.py` — modelos Pydantic (entrada, saída e enums).
- `prompts.py` — prompt de sistema e schema da ferramenta.
- `classifier.py` — chamada ao modelo e validação da resposta.

**Fluxo n8n (`n8n/workflow.json`)**

| Node | Função |
|---|---|
| Webhook | Recebe `POST /webhook/mensagem` com `mensagem`, `remetente`, `canal` |
| Edit Fields | Extrai e padroniza os campos e registra `recebido_em` |
| HTTP Request (API + IA) | Chama `http://api:8000/classificar` |
| Switch (por setor) | Roteia conforme `setor`; o *fallback* vai ao Atendimento Geral |
| Encaminhar … (×4) | Define fila, e-mail de destino e texto da notificação |
| Respond to Webhook | Devolve o JSON final ao solicitante |

> Os nodes "Encaminhar" simulam o envio (definem destino e notificação). Em produção basta trocá-los por Slack, Gmail, Google Sheets, Trello etc.

📸 Prints do fluxo: veja [`docs/PRINTS.md`](docs/PRINTS.md).

## 6. Como Executar

### Pré-requisitos
- Docker e Docker Compose **ou** Python 3.10+
- Uma chave de API do Google Gemini, gratuita em https://aistudio.google.com/apikey

### Opção A — Docker Compose (API + n8n)

```bash
git clone <URL_DO_SEU_REPOSITORIO>
cd <pasta>
cp .env.example .env        # edite e coloque sua GEMINI_API_KEY
docker compose up --build
```

- API: http://localhost:8000 (documentação interativa em `/docs`)
- n8n: http://localhost:5678 (crie a conta local no primeiro acesso)

**Importar o fluxo no n8n**
1. No n8n: menu **⋯ → Import from File…** e escolha `n8n/workflow.json`
   (dentro do container o arquivo também está em `/files/workflow.json`).
2. Clique em **Publish/Activate** para ativar o workflow.

### Opção B — Somente a API (sem Docker)

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                  # coloque sua chave
uvicorn app.main:app --reload
```

Teste direto:

```bash
curl -X POST http://localhost:8000/classificar \
  -H "Content-Type: application/json" \
  -d '{"mensagem":"Fui cobrado duas vezes!","remetente":"maria@email.com","canal":"email"}'
```

### Testando o fluxo completo

Com o workflow ativo, rode `./exemplos.sh` (envia 4 mensagens, uma para cada setor).
Para testar com o botão **Execute workflow** do n8n (para tirar prints), use `./exemplos.sh test`, que chama a URL `/webhook-test/`.

### Testes automatizados

```bash
pip install -r requirements-dev.txt
pytest
```

## Estrutura do repositório

```
├── app/                 # API FastAPI
├── n8n/workflow.json    # Fluxo exportado do n8n
├── docs/                # Documentação visual (prints)
├── tests/               # Testes da API
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── exemplos.sh
└── README.md
```

## Segurança

Nenhuma credencial é versionada: a chave fica no `.env` (ignorado pelo Git); apenas o `.env.example` está no repositório.
