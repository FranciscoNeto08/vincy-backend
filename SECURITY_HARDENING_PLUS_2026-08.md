# Vynce — Hardening adicional

Esta revisão adiciona camadas de segurança de baixo risco de regressão:

- validação de HS256 como único algoritmo JWT da versão atual;
- validação de formato da chave Fernet no startup de produção;
- FRONTEND_URL obrigatória em HTTPS e ALLOWED_ORIGINS sem wildcard/HTTP em produção;
- validação de X-Request-ID antes de refletir no response;
- COOP, CORP, Origin-Agent-Cluster e X-Permitted-Cross-Domain-Policies;
- rate limiter com buckets de cardinalidade controlada;
- escape de nome em e-mail transacional;
- remoção de detalhes internos em erro da Evolution API;
- allowlist https://wa.me para links renderizados no frontend;
- remoção da versão do endpoint público raiz.

## Próximos passos arquiteturais (não aplicados para evitar regressão na V1)

1. hospedar a API em `api.vynce.tech`;
2. migrar autenticação para cookie HttpOnly + Secure + SameSite e proteção CSRF;
3. migrar o Financeiro Mensal atualmente local para PostgreSQL;
4. substituir rate limiting em memória por Redis/Cloudflare WAF ao escalar;
5. adicionar testes multi-tenant automatizados para todos os CRUDs;
6. adicionar rotina testada de backup/restore e monitoramento de dependências.
