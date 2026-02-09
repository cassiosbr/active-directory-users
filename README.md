# Usuários do Active Directory (AD)

API em FastAPI para consultar dados de usuários no Active Directory (Microsoft Entra ID) via Microsoft Graph.

Ela expõe endpoints para:

- Buscar dados básicos do usuário por Email ou UPN (User Principal Name)
- Buscar a foto do usuário (binário `image/*`)

## Requisitos

- Python 3.10+
- Credenciais de aplicação (Client Credentials) com permissões no Microsoft Graph

## Configuração (variáveis de ambiente)

O projeto lê configurações de um arquivo `.env` na raiz do repositório.

Crie um `.env` com:

```env
# Protege as rotas /users-active-directory e /users-active-directory-photo
X_API_KEY=troque-esta-chave

# Microsoft Graph (Client Credentials)
MICROSOFT_GRAPH_TENANT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
MICROSOFT_GRAPH_CLIENT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
MICROSOFT_GRAPH_CLIENT_SECRET=seu-secret

# Base da API e OAuth
MICROSOFT_GRAPH_API=https://graph.microsoft.com/v1.0
MICROSOFT_GRAPH_SCOPE=https://graph.microsoft.com/.default
MICROSOFT_GRAPH_AUTHORITY=https://login.microsoftonline.com
```

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Executando

```bash
python -m uvicorn main:app --app-dir src --host 0.0.0.0 --port 8000 --reload
```

Abra a documentação interativa:

- http://localhost:8000/docs

## Autenticação (x_api_key)

As rotas que consultam o Active Directory exigem o header `x_api_key` com o mesmo valor configurado em `X_API_KEY`.

## Endpoints

- `GET /api/v1/health`
- `GET /api/v1/users` (mock)
- `GET /api/v1/users-active-directory?email=...` (protegido por `x_api_key`)
- `GET /api/v1/users-active-directory-photo?email=...` (protegido por `x_api_key`, retorna `image/*`)

### Exemplos com curl

Buscar usuário:

```bash
curl -H "x_api_key: $X_API_KEY" \
	"http://localhost:8000/api/v1/users-active-directory?email=usuario@empresa.com"
```

Buscar foto (salvando em arquivo):

```bash
curl -H "x_api_key: $X_API_KEY" \
	"http://localhost:8000/api/v1/users-active-directory-photo?email=usuario@empresa.com" \
	--output foto.jpg
```