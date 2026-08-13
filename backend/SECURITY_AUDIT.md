# Auditoria de Segurança - Vynce

## Escopo

Rodada de hardening aplicada ao backend FastAPI, integração Evolution API/WhatsApp, campanhas de marketing, webhooks e rotinas operacionais.

## Controles confirmados

1. Isolamento multi-tenant por `owner_id` nas entidades de negócio.
2. Revalidação de referências entre entidades para reduzir BOLA/IDOR.
3. Senhas com Argon2id e compatibilidade para hashes bcrypt legados.
4. Invalidação de sessões por versão de token em operações sensíveis.
5. Rate limiting global e específico para autenticação/campanhas.
6. Limite de tamanho do corpo das requisições.
7. CORS, TrustedHost e security headers configuráveis.
8. OpenAPI desativado quando `DEBUG=false`.
9. Auditoria de ações críticas sem registrar senhas, tokens ou API keys.
10. Conteúdo de marketing escapado antes de ser inserido em HTML.
11. Limites de tamanho e quantidade nos schemas.

## Correções desta rodada

### Evolution API / SSRF
- `base_url` é validada antes de ser salva e antes de cada chamada.
- Endereços privados, loopback, link-local, multicast, reservados e não especificados são rejeitados por padrão.
- `EVOLUTION_ALLOW_PRIVATE_TARGETS` existe somente para desenvolvimento e é proibido em produção.
- URLs de mídia também passam pela validação.
- Respostas de erro da Evolution não retornam o corpo bruto ao cliente.

### Segredos
- API Key da Evolution não é devolvida pelo endpoint de configuração.
- `.env` não deve ser versionado.
- `.env.example` contém apenas placeholders.
- Auditoria de histórico Git foi incluída em `scripts/audit_git_secrets.ps1`.

### Campanhas
- Limite de destinatários por campanha.
- Limite diário por proprietário.
- Rate limiting por usuário.
- Payload da campanha WhatsApp usa schema Pydantic, evitando parâmetros soltos.
- Campanhas são registradas para auditoria operacional.
- Falhas retornam mensagens genéricas ao cliente.

### E-mail marketing
- Clientes podem cancelar inscrições.
- Token de descadastro usa HMAC e não exige tabela adicional.
- E-mails de marketing incluem link de descadastro.
- Headers `List-Unsubscribe` e `List-Unsubscribe-Post` são enviados.
- Clientes marcados como `unsubscribed` são excluídos de novas campanhas.
- Eventos `email.bounced` e `email.complained` do Resend podem marcar o cliente como descadastrado após validação Svix.

### Banco e operação
- Migration Alembic adiciona `clients.unsubscribed`.
- Scripts de backup/restore PostgreSQL usam variáveis de ambiente e não armazenam senhas no código.

## Testes incluídos

`backend/tests/test_security_basics.py` cobre, entre outros:
- rejeição de loopback/private IP em SSRF;
- geração e validação de token HMAC;
- detecção de adulteração do token.

Execute:

```powershell
cd backend
pip install -r requirements-dev.txt
pytest
```

## Limitações

- O rate limiting em memória é adequado para desenvolvimento ou uma única instância. Em produção horizontal, use Redis ou outro armazenamento compartilhado.
- SSRF por hostname depende da resolução DNS observada durante a validação. Para ambientes de altíssimo risco, prefira uma camada de egress/firewall ou um cliente HTTP que fixe a resolução IP.
- O webhook do Resend precisa ser configurado no painel do Resend com o segredo Svix correspondente.
- Credenciais que já tenham sido expostas no histórico Git devem ser revogadas e rotacionadas. Remover o arquivo do último commit não revoga uma chave que já vazou.

## Resultado

O projeto foi preparado para uma nova rodada de testes e implantação, mas segurança não é um botão de “100% concluído”. Dependências, infraestrutura, configuração de produção e integrações externas continuam exigindo revisão periódica.
