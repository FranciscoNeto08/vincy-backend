# Vynce — hardening de segurança da V1

## Alterações aplicadas

- Escapagem central de HTML em valores vindos da API antes de uso em `innerHTML` no dashboard.
- Mensagens dinâmicas da integração WhatsApp renderizadas com `textContent`.
- CSP e demais headers de segurança no Cloudflare Pages via `frontend/_headers`.
- Script inline de tema movido para `frontend/theme-init.js`, permitindo bloquear JavaScript inline no CSP.
- Estilos inline do `<head>` movidos para `dashboard.css`.
- `TrustedHostMiddleware` passa a derivar automaticamente o hostname de `BACKEND_PUBLIC_URL` quando `ALLOWED_HOSTS` não foi configurado.
- Favicon e metadado de referrer adicionados às páginas.
- `docker-compose.yml` atualizado para refletir variáveis de segurança exigidas pela aplicação.
- `.env.example` seguro incluído; o pacote de distribuição NÃO contém `.env` real, histórico `.git`, `.vscode` ou testes locais com credenciais.

## Controles já existentes e preservados

- Argon2 para senhas, migração de bcrypt legado.
- JWT com expiração, issuer, audience, jti e token_version.
- Verificação de e-mail, reset com token de uso único e hash no banco.
- Bloqueio de força bruta e rate limiting.
- CORS restrito, HTTPS/HSTS, limite de corpo, headers de segurança do backend.
- Isolamento multi-tenant por `owner_id`.
- Proteção SSRF na Evolution API.
- Webhook Resend validado criptograficamente.
- Credencial da Evolution API criptografada em repouso.

## Observação arquitetural

O token de sessão permanece no `localStorage` para preservar o funcionamento atual entre abas e o frontend estático hospedado em domínio separado do backend Render. O risco foi reduzido com a correção dos sinks XSS e CSP estrita de scripts. A evolução recomendada é migrar autenticação para cookie HttpOnly + Secure + SameSite quando o backend estiver em domínio próprio (por exemplo `api.vynce.tech`) e houver fluxo CSRF testado, evitando uma migração apressada que possa quebrar login em navegadores com bloqueio de cookies de terceiros.

O Financeiro Mensal ainda usa armazenamento local para parte dos dados da interface. A migração para PostgreSQL é uma melhoria de arquitetura/sincronização, mas foi deliberadamente evitada neste hardening para não alterar o modelo funcional da V1 sem uma rodada específica de migração e testes.

## Testes executados

- `node --check` nos JavaScript alterados.
- `python -m compileall` no backend.
- `pytest`: 4 testes aprovados.
