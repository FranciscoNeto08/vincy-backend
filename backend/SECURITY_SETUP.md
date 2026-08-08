# Vynce — checklist obrigatório de segurança

Esta versão endurece o backend sem trocar o fluxo atual de Bearer Token do frontend.
Nenhum sistema é "inatingível"; o objetivo é defesa em profundidade e redução mensurável de risco.

## 1. Antes do deploy

No Render, configure as variáveis de ambiente do `.env.example`.

A mais importante é `SECRET_KEY`. Gere uma nova no seu computador:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Cole o resultado no Render como `SECRET_KEY`. Nunca envie essa chave por GitHub, print ou mensagem.

Use `DEBUG=false` em produção.

Configure `FRONTEND_URL` e `ALLOWED_ORIGINS` somente com o domínio real do frontend, usando HTTPS.

## 2. Deploy / banco

O Dockerfile já executa:

```text
alembic upgrade head
```

A migration `e5a9b8c7d612_security_hardening.py` adiciona versionamento de sessão e logs de auditoria.

Faça backup do PostgreSQL antes do primeiro deploy desta versão.

## 3. O que esta versão protege

- Argon2 para novas senhas.
- Migração automática de senhas bcrypt antigas após login válido.
- JWT com expiração curta, issuer, audience, jti e versão de sessão.
- Troca/reset de senha invalida JWTs emitidos anteriormente.
- Reset tokens novos ficam armazenados apenas como SHA-256 no banco.
- Tokens de e-mail são de uso único e tokens anteriores são invalidados.
- Rate limit por IP na API e limites mais fortes em autenticação/recuperação.
- Rate limit por usuário em campanhas.
- Tamanho máximo de payload.
- CORS restrito.
- TrustedHost opcional.
- Headers de segurança e HSTS em produção.
- Swagger/OpenAPI desligados em produção.
- Auditoria de login, reset, perfil e campanhas.
- Verificação `owner_id` em referências de cliente/serviço/comanda.
- Mudança de e-mail exige nova verificação.
- Desativação de usuário invalida sessões.
- Escape de conteúdo de campanha antes de inserir em HTML.
- Limites de tamanho/intervalo nos schemas Pydantic.

## 4. O que ainda depende da infraestrutura

Para segurança de nível comercial, configure também fora do código:

- backups automáticos e teste real de restauração;
- proteção/WAF/rate limiting na borda (Cloudflare ou equivalente);
- alertas de erro e disponibilidade;
- rotação periódica de API keys;
- conta do GitHub com 2FA e proteção da branch `main`;
- acesso ao Render com 2FA;
- banco sem exposição pública desnecessária;
- revisão periódica de dependências;
- pentest antes de clientes de alto risco/regulados.

O rate limit incluído no código é por processo. Se futuramente houver múltiplas instâncias do backend, mova esse estado para Redis ou para um WAF/gateway centralizado.

## 5. Compatibilidade importante

O frontend atual usa Bearer JWT. Isto foi mantido para não quebrar o SaaS.
Uma etapa futura pode migrar autenticação para cookies HttpOnly + proteção CSRF, mas isso exige alteração coordenada no frontend e backend e não deve ser feita como simples troca de arquivos.
