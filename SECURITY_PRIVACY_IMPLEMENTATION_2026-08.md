# Vynce — Segurança, Privacidade e Governança de Dados

Versão técnica: 2026-08

## Objetivo
Este documento registra os controles implementados nesta versão do Vynce para segurança, LGPD, aceite de documentos legais, permissões de marketing, retenção e exclusão de dados.

## Aceite versionado
- Tabela: `legal_acceptances`.
- O backend registra `user_id`, tipo do documento, versão vigente, data/hora, IP, user-agent e request ID.
- O frontend não define a versão aceita. A versão é controlada por `TERMS_VERSION` e `PRIVACY_VERSION` no backend.
- Novos cadastros exigem aceite dos Termos e ciência da Política de Privacidade.
- Usuários antigos sem aceite vigente recebem HTTP 428 nas rotas de negócio e são direcionados para `legal-consent.html`.
- Rotas de autenticação/bootstrap continuam acessíveis para permitir o aceite.

## Marketing por canal
- Tabela: `client_marketing_permissions`.
- A permissão é independente por `email` e `whatsapp`.
- O cadastro do contato não autoriza marketing automaticamente.
- São registrados status, origem, observação/base legal, data de captura e data de revogação.
- Campanhas filtram no backend somente destinatários com permissão positiva para o canal.
- Descadastro por link e eventos de complaint/bounce do Resend revogam o canal e-mail.

## Retenção
- Tokens de e-mail expirados: retenção técnica padrão de 30 dias após expiração (`EXPIRED_TOKEN_RETENTION_DAYS`).
- Audit logs: retenção padrão de 180 dias (`AUDIT_LOG_RETENTION_DAYS`). Ajustar conforme decisão jurídica/regulatória.
- Dados operacionais: mantidos enquanto a conta estiver ativa, salvo exclusão solicitada ou obrigação legal aplicável.
- Rotina administrativa: `POST /privacy/retention/cleanup` (admin).
- A rotina deve ser acionada periodicamente por processo administrativo/cron autorizado.

## Direitos do titular
- `GET /privacy/export-me`: exporta dados da conta sem senha, hashes, tokens ou segredos de integração.
- `POST /privacy/delete-my-account`: exclusão permanente com senha atual + frase de confirmação.
- Contas administrativas não podem ser excluídas por autoatendimento.
- Logs de auditoria vinculados à conta são desvinculados antes da exclusão, preservando apenas o mínimo necessário para segurança.

## Segurança de aplicação
- Senhas novas: Argon2; bcrypt apenas para migração de hashes antigos.
- JWT: algoritmo fixado em HS256, `iss`, `aud`, `exp`, `jti` e `token_version`.
- Troca/reset de senha invalida tokens anteriores.
- Rate limiting por IP no backend, mais limites específicos para recuperação de senha e campanhas.
- CORS apenas com origens HTTPS explícitas em produção.
- TrustedHost derivado de `BACKEND_PUBLIC_URL` quando `ALLOWED_HOSTS` não é informado.
- Limite de payload, CSP no backend, HSTS e headers de proteção.
- Frontend com `_headers` para Cloudflare Pages, CSP e anti-framing.
- Dados dinâmicos exibidos via escape/textContent nos pontos de maior risco de XSS.
- SSRF protection na Evolution API.
- Credenciais da Evolution criptografadas com Fernet; chave mestra apenas no ambiente.
- Webhooks Resend autenticados por assinatura/timestamp.
- `.env`, bancos locais, chaves e arquivos de teste sensíveis são ignorados pelo Git.

## Pendências empresariais antes da venda
1. Preencher razão social/CNPJ/endereço no texto legal definitivo.
2. Definir e disponibilizar canal oficial de privacidade/DPO/encarregado, conforme aplicável.
3. Revisar com advogado Termos, Política, foro e bases legais de marketing.
4. Formalizar/arquivar DPAs dos fornecedores e mecanismo de transferência internacional.
5. Definir prazo final de retenção de dados operacionais e fiscais conforme o negócio.
6. Configurar agendamento periódico da rotina de retenção.
7. Executar testes de carga e testes de autorização entre duas contas antes de escala.

## Regra de publicação
`termos.html` e `privacidade.html` incluídos neste pacote estão marcados como versão de homologação. Não remover essa marcação nem publicar como documento contratual definitivo antes de preencher os dados empresariais e obter revisão jurídica.
