# Vynce V1 — publicação final

## 1. Render: novas variáveis obrigatórias
Adicione no backend:

- `SUBSCRIPTION_ADMIN_KEY`: segredo aleatório com 32+ caracteres. Nunca colocar no frontend/GitHub.
- `OWNER_CONTACT`: canal comercial exibido/administrado pela operação.
- `LEGAL_TERMS_VERSION=1.0-2026-08-18`
- `LEGAL_PRIVACY_VERSION=1.0-2026-08-18`

O comando de deploy já deve executar `python -m alembic upgrade head` antes do Uvicorn.

## 2. Liberação após pagamento externo
O pagamento NÃO ocorre dentro da Vynce. Após confirmar o Pix/contratação, o responsável ativa a conta pelo backend.

Exemplo PowerShell (NÃO compartilhe a chave):

```powershell
$headers = @{ "X-Vynce-Admin-Key" = "SUA_CHAVE_DO_RENDER" }
$body = @{ email = "cliente@empresa.com"; days = 30 } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "https://vincy-backend-u43m.onrender.com/subscriptions/activate" -Headers $headers -ContentType "application/json" -Body $body
```

Para bloquear:

```powershell
$headers = @{ "X-Vynce-Admin-Key" = "SUA_CHAVE_DO_RENDER" }
$body = @{ email = "cliente@empresa.com"; days = 30 } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "https://vincy-backend-u43m.onrender.com/subscriptions/block" -Headers $headers -ContentType "application/json" -Body $body
```

## 3. Conta antiga do dono
A migration marca contas existentes como `pending`. Depois do deploy, libere a sua própria conta usando o mesmo endpoint acima.

## 4. Cloudflare Pages
Publique a pasta `frontend/` completa. Ela contém `termos.html`, `privacidade.html` e `feedback.html`.

## 5. Fluxo implementado
Cadastro -> checkbox legal obrigatório -> registro versionado do aceite -> confirmação de e-mail -> login -> tela bloqueada/blur -> contato e pagamento externo -> ativação administrativa -> uso do SaaS.

Ao finalizar uma comanda, é criado um link de feedback temporário e de uso único. O link é copiado para a área de transferência quando permitido pelo navegador.
