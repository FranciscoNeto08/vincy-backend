FROM python:3.12-slim

WORKDIR /app

# Dependências do sistema necessárias para psycopg2/bcrypt
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Aplica as migrations do banco antes de subir o servidor. Sem isso, colunas
# e tabelas novas (ex: employee_id, appointments, campaigns, email_tokens)
# nunca são criadas no banco de produção, e a API quebra com erros do tipo
# "column does not exist".
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --no-server-header"]
