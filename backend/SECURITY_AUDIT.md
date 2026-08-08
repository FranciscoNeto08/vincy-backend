# Auditoria aplicada — Vynce Security Max

## Achados relevantes no código recebido

1. O isolamento por `owner_id` já existia na maior parte das rotas e serviços.
2. `AppointmentUpdate` aceitava trocar `client_id`/`service_id` sem revalidar que o novo ID pertencia ao mesmo `owner_id`. Corrigido.
3. `TransactionCreate.comanda_id` podia apontar para uma comanda sem validar o `owner_id`. Corrigido.
4. Senhas novas usavam bcrypt. Novas senhas passam a Argon2; hashes bcrypt existentes continuam funcionando e são migrados no login.
5. JWTs não tinham versão de sessão. Agora troca/reset/desativação invalida tokens antigos.
6. Tokens de reset/confirmação eram guardados em texto puro. Novos tokens passam a ser guardados por digest SHA-256 e continuam de uso único.
7. Não havia limite geral de requisições/payload. Foram adicionados rate limits e limite de corpo.
8. CORS já era configurável, mas métodos/headers estavam amplos. Foram restringidos.
9. Documentação OpenAPI fica desligada em produção.
10. Foram adicionados security headers, request IDs e logs de auditoria para ações críticas.
11. Conteúdo de marketing enviado por e-mail agora é escapado antes de entrar no HTML.
12. Schemas receberam limites de comprimento, quantidade e valores para reduzir abuso de recursos.

## Compatibilidade preservada

- URLs principais das rotas foram mantidas.
- Bearer JWT foi mantido para não quebrar o frontend atual.
- Estrutura multi-tenant baseada no usuário logado foi mantida.
- Resend e WhatsApp continuam no mesmo fluxo funcional.
- Senhas bcrypt antigas continuam válidas.
