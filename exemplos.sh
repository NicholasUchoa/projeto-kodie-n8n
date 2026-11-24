#!/usr/bin/env bash
# Envia mensagens de exemplo ao webhook do n8n.
# Uso: ./exemplos.sh [test|prod]   (test = /webhook-test/, prod = /webhook/)
MODO="${1:-prod}"
BASE="http://localhost:5678/webhook"; [ "$MODO" = "test" ] && BASE="http://localhost:5678/webhook-test"
URL="$BASE/mensagem"

enviar() { echo "--- $1"; curl -s -X POST "$URL" -H "Content-Type: application/json" -d "$2"; echo; }

enviar "Financeiro" '{"mensagem":"Fui cobrado duas vezes no cartão este mês e preciso do estorno urgente!","remetente":"maria@email.com","canal":"email"}'
enviar "Suporte"    '{"mensagem":"O aplicativo fecha sozinho toda vez que tento abrir o relatório.","remetente":"joao@email.com","canal":"whatsapp"}'
enviar "Comercial"  '{"mensagem":"Gostaria de um orçamento do plano empresarial para 20 usuários.","remetente":"ana@empresa.com","canal":"site"}'
enviar "Geral"      '{"mensagem":"Parabéns pelo atendimento de vocês, fui muito bem atendido!","remetente":"carlos@email.com","canal":"email"}'
