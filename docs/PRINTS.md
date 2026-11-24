# Documentação visual do fluxo n8n

> Substitua cada placeholder pelo seu print (salve as imagens em `docs/prints/`).
> Dica: nomeie os arquivos como indicado abaixo para manter tudo organizado.

## 1. Fluxo completo
Todos os nodes conectados: Webhook → Edit Fields → HTTP Request → Switch → 4 nodes de encaminhamento → Respond to Webhook.

![Fluxo completo](prints/01-fluxo-completo.png)

## 2. Execução bem-sucedida
Execução concluída com sucesso (aba **Executions**, status *Succeeded*).

![Execução com sucesso](prints/02-execucao-sucesso.png)

## 3. Configuração dos nodes

| Node | O que mostrar | Print |
|---|---|---|
| **Webhook** | Método POST, path `mensagem`, *Respond: Using 'Respond to Webhook' Node* | `prints/03-node-webhook.png` |
| **Edit Fields** | Campos `mensagem`, `remetente`, `canal`, `recebido_em` | `prints/04-node-edit-fields.png` |
| **HTTP Request (API + IA)** | POST `http://api:8000/classificar` e o JSON body | `prints/05-node-http-request.png` |
| **Switch (por setor)** | Regras por `setor` + saída *fallback* | `prints/06-node-switch.png` |
| **Encaminhar (qualquer um)** | Campos `setor_destino`, `canal_encaminhamento`, `email_destino`, `notificacao` | `prints/07-node-encaminhar.png` |
| **Respond to Webhook** | Resposta JSON com `{{ $json }}` | `prints/08-node-respond.png` |

## 4. Resultados em cada etapa
Abra uma execução e mostre os dados (aba *Output*) de:

1. **Webhook** (payload recebido) → `prints/09-resultado-webhook.png`
2. **HTTP Request** (JSON classificado pela IA) → `prints/10-resultado-ia.png`
3. **Switch** (qual saída foi usada) → `prints/11-resultado-switch.png`
4. **Encaminhar** (dados finais) → `prints/12-resultado-encaminhar.png`
5. **Teste via curl/Postman** com a resposta final → `prints/13-resposta-final.png`
