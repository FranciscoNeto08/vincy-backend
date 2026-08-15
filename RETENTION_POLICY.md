# Política Técnica de Retenção — Vynce

## Padrões implementados
- Tokens expirados de confirmação/reset: exclusão após 30 dias da expiração.
- Audit logs: 180 dias por padrão.
- Credenciais de integração: enquanto a integração estiver ativa; removidas com a conta.
- Dados operacionais (clientes, comandas, agenda, serviços, equipe, campanhas e transações): enquanto a conta estiver ativa, até solicitação válida de exclusão ou política legal definida.
- Dados no `localStorage`: persistem no dispositivo até logout/limpeza/alteração; não substituem a política de retenção do backend.

## Exclusão de conta
A exclusão permanente remove dados operacionais e credenciais do banco. Logs de auditoria são desvinculados de identificadores da conta antes da exclusão quando sua preservação mínima for necessária para segurança.

## Operação
Executar periodicamente `POST /privacy/retention/cleanup` com credencial administrativa. Recomenda-se agendamento diário ou semanal em ambiente de produção.

## A definir juridicamente
- Retenção fiscal/contábil.
- Retenção após encerramento contratual.
- Prazo de backups e processo de expurgo de backups.
- Retenção de incidentes conforme obrigações regulatórias aplicáveis.
