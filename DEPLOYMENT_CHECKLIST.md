# Checklist de publicação segura

## Backend / Render
- [ ] `DEBUG=false`
- [ ] `DATABASE_URL` de produção configurada
- [ ] `SECRET_KEY` aleatória, longa e exclusiva
- [ ] `CREDENTIAL_ENCRYPTION_KEY` Fernet válida e guardada fora do Git
- [ ] `FRONTEND_URL=https://vynce.tech`
- [ ] `BACKEND_PUBLIC_URL` HTTPS
- [ ] `ALLOWED_ORIGINS` somente origens HTTPS necessárias
- [ ] `ALLOWED_HOSTS` configurado ou derivado da URL pública
- [ ] `RESEND_API_KEY` e webhook secret no Environment
- [ ] `TERMS_VERSION=1.0`
- [ ] `PRIVACY_VERSION=1.0`
- [ ] `ENFORCE_LEGAL_ACCEPTANCE=true`
- [ ] `alembic upgrade head` concluído
- [ ] Deploy terminou com `Application startup complete`

## Frontend / Cloudflare
- [ ] Publicar toda a pasta `frontend/`
- [ ] Confirmar que `_headers` foi publicado
- [ ] Testar CSP sem erros críticos no Console
- [ ] Testar cadastro com aceite legal
- [ ] Testar usuário antigo sendo enviado para `legal-consent.html`
- [ ] Testar cliente com e sem permissão de marketing
- [ ] Confirmar que campanha ignora contatos sem permissão
- [ ] Testar exportação de dados
- [ ] Testar exclusão somente em conta de homologação

## Jurídico/operacional
- [ ] Razão social e CNPJ preenchidos
- [ ] Endereço oficial preenchido
- [ ] Canal de privacidade/DPO definido
- [ ] Termos e Política revisados por profissional jurídico
- [ ] DPAs de Cloudflare, Render e Resend arquivados
- [ ] Transferência internacional documentada
- [ ] Foro definido com assessoria jurídica
- [ ] Prazos definitivos de retenção aprovados
- [ ] Rotina `/privacy/retention/cleanup` agendada
