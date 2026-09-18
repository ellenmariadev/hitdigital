# HitDigital - Consulta de Usuários (Backend + Frontend)

Aplicação full-stack que recebe uma lista de IDs, consulta cada usuário em uma **API HTTP
externa de forma assíncrona** e devolve separadamente os usuários obtidos e os IDs que
falharam. Uma falha individual (não encontrado, timeout ou erro HTTP) **não interrompe** o
processamento dos demais.

- **Backend**: API em Python/FastAPI com o endpoint `POST /api/users/fetch`, cache de
  usuários no PostgreSQL e logs estruturados.
- **Frontend**: interface em React + TypeScript (Vite) que informa os IDs, executa a
  consulta e exibe *loading*, usuários encontrados, IDs que falharam e o erro do backend.

---

## Sumário

- [Stack](#stack)
- [Estrutura](#estrutura)
- [Como executar](#como-executar)
- [API](#api)
- [Configuração (variáveis de ambiente)](#configuração-variáveis-de-ambiente)
- [Decisões técnicas](#decisões-técnicas)
- [Testes](#testes)
- [O que melhoraria com mais tempo](#o-que-melhoraria-com-mais-tempo)
- [Uso de IA](#uso-de-ia)
- [E se precisasse consultar milhares de usuários?](#e-se-precisasse-consultar-milhares-de-usuários)
- [Próximos passos](#próximos-passos)

---

## Stack

**Backend**

| Camada | Escolha |
| --- | --- |
| Linguagem | Python 3.12 |
| Framework | FastAPI + Uvicorn |
| Gerenciador de pacotes | [uv](https://docs.astral.sh/uv/) (`pyproject.toml` + `uv.lock`) |
| HTTP client | httpx (assíncrono) |
| Configuração | pydantic-settings (`.env`) |
| Banco | PostgreSQL 17 (via Docker) + SQLAlchemy async/asyncpg (cache de usuários) |
| Migrations | Alembic |
| Observabilidade | structlog (logs JSON com `request_id`) |
| Qualidade | Ruff (lint/format) e mypy |
| Testes | pytest |
| CI | GitHub Actions |
| Container | Docker + docker-compose |

**Frontend**

| Camada | Escolha |
| --- | --- |
| Linguagem | TypeScript |
| Framework | React 18 + Vite |
| Estilo | CSS Modules (sem biblioteca de UI) |
| HTTP | `fetch` nativo |
| Estado | Hooks (`useUserSearch`) + estado de UI explícito |
| Qualidade | `tsc --noEmit` (strict) |

---

## Estrutura

```
.
├── README.md                       # este arquivo (único README do projeto)
├── backend/
│   ├── app/
│   │   ├── main.py                 # app factory, lifespan, include_router, /health
│   │   ├── config/
│   │   │   ├── settings.py         # configuração tipada (.env)
│   │   │   ├── logging.py          # logging estruturado (structlog/JSON)
│   │   │   └── exceptions.py       # ProviderError / UserNotFoundError
│   │   ├── db/
│   │   │   ├── base.py             # DeclarativeBase (metadata p/ Alembic)
│   │   │   ├── session.py          # engine asyncpg (pool) + session factory + ping
│   │   │   └── models/user.py      # ORM da tabela users (cache)
│   │   ├── models/user.py          # request/response + validação (Pydantic)
│   │   ├── repositories/user_repository.py  # SQL: get_valid / upsert / delete_expired
│   │   ├── cache/                  # cache plugável
│   │   │   ├── base.py             #   Protocol UserCache
│   │   │   ├── memory.py           #   in-memory TTL (testes/dev)
│   │   │   └── postgres.py         #   cache no PostgreSQL
│   │   ├── providers/              # integração externa isolada
│   │   │   ├── base.py             #   Protocol UserProvider
│   │   │   ├── jsonplaceholder.py  #   provider HTTP real
│   │   │   └── fake.py             #   provider in-memory (dev/testes)
│   │   ├── services/user_service.py# regra de negócio (cache-aside + fan-out assíncrono)
│   │   └── api/users.py            # POST /api/users/fetch (+ dependências)
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_users_endpoint.py
│   │   ├── test_provider.py
│   │   └── integration/test_user_cache_pg.py
│   ├── alembic/                    # migrations do schema
│   ├── scripts/entrypoint.sh       # alembic upgrade head + uvicorn
│   ├── docker-compose.yml
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── .env.example
└── frontend/
    ├── index.html
    ├── package.json
    ├── tsconfig.json
    ├── vite.config.ts              # proxy /api -> http://localhost:8000
    ├── .env.example
    └── src/
        ├── main.tsx                # bootstrap do React
        ├── App.tsx                 # composição da tela
        ├── styles/global.css       # reset + design tokens
        ├── api/
        │   ├── userApi.ts          # fetchUsers() -> POST /api/users/fetch
        │   └── errors.ts           # ApiError
        ├── config/env.ts           # API_BASE_URL, MAX_USER_IDS, ...
        ├── types/user.ts           # User, FetchUsersResponse
        ├── utils/parseUserIds.ts   # parse/validação/deduplicação/limite
        ├── hooks/
        │   ├── useUserSearch.ts    # idle -> loading -> success | error
        │   └── useElapsedSeconds.ts
        └── components/
            ├── common/             # Alert, Badge, Button, Card, Icon, Layout, Spinner
            ├── UserSearchForm/     # entrada de IDs + validação + contador
            ├── UserCardList/       # grade de usuários ("Mostrar mais")
            ├── UserCard/           # card de usuário (memo)
            └── FailedIdList/       # IDs que falharam (badges)
```

---

## Como executar

Pré-requisitos: **Docker + docker-compose**, **uv** (backend) e **Node.js 18+** (frontend).

### Backend - Opção A: Docker Compose (recomendado)

Sobe o PostgreSQL e a API juntos (as migrations rodam no entrypoint):

```bash
cd backend
cp .env.example .env          
docker-compose up -d --build
```

Verifique:

```bash
curl localhost:8000/health          # {"status":"ok"}
curl localhost:8000/health/db       # {"database":"ok"}
```

Parar: `docker-compose down`.

### Backend - Opção B: local (uv + Postgres em Docker)

```bash
cd backend
uv sync --all-groups
docker-compose up -d db
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

A API fica em `http://localhost:8000` (Swagger em `/docs`).

Nova migration após mudar o schema:

```bash
uv run alembic revision --autogenerate -m "descrição"
uv run alembic upgrade head
```

### Frontend

Com o backend no ar em `http://localhost:8000`:

```bash
cd frontend
yarn install        # ou: npm install
yarn dev            # ou: npm run dev
```

Abra `http://localhost:5173`. Em desenvolvimento o Vite faz **proxy de `/api`** para o
backend (`vite.config.ts`), então **não há CORS** e nenhuma configuração extra é necessária.

Outros scripts:

```bash
yarn build       # tsc --noEmit + build de produção em dist/
yarn preview     # serve o build de produção
yarn typecheck   # apenas a checagem de tipos
```

---

## API

### `POST /api/users/fetch`

**Request**

```json
{ "user_ids": [1, 2, 3, 4] }
```

- `user_ids` deve ser uma lista **não vazia** de inteiros **positivos**.
- IDs duplicados são removidos preservando a ordem.
- Limite máximo configurável (`MAX_USER_IDS`, padrão 500).

**Response** `200 OK`

```json
{
  "users": [
    { "id": 1, "name": "Leanne Graham", "email": "Sincere@april.biz", "username": "Bret" }
  ],
  "failed": [999],
  "errors": [{ "id": 999, "reason": "not_found" }]
}
```

- `users`: usuários encontrados.
- `failed`: IDs que falharam (não encontrado, timeout ou erro HTTP).
- `errors`: motivo por ID — `not_found` (404) ou `provider_error` (timeout/erro HTTP).
  *(Pequena variação aceitável do formato conceitual; `failed` é preservado.)*

**Exemplo**

```bash
curl -X POST localhost:8000/api/users/fetch \
  -H 'content-type: application/json' \
  -d '{"user_ids":[1,2,999]}'
```

**Erros de validação** retornam `422` (lista vazia, IDs não positivos ou acima do limite).

### Outros endpoints

| Método | Rota | Descrição |
| --- | --- | --- |
| GET | `/health` | Liveness da aplicação |
| GET | `/health/db` | Conectividade com o PostgreSQL (`503` se indisponível) |
| GET | `/docs` | Swagger UI |

---

## Configuração (variáveis de ambiente)

### Backend (`backend/.env`, veja `backend/.env.example`)

Variáveis de ambiente do processo têm precedência sobre o arquivo `.env`.

| Variável | Padrão | Descrição |
| --- | --- | --- |
| `DATABASE_URL` | — (**obrigatória**) | Conexão com o PostgreSQL |
| `DB_ECHO` | `false` | Loga SQL do SQLAlchemy |
| `DB_POOL_SIZE` | `5` | Conexões do pool |
| `DB_MAX_OVERFLOW` | `10` | Conexões extras acima do pool |
| `DB_POOL_RECYCLE_SECONDS` | `1800` | Recicla conexões antigas |
| `DEBUG` | `false` | Nível de log (DEBUG/INFO) |
| `USER_PROVIDER` | `jsonplaceholder` | Provider externo: `jsonplaceholder` ou `fake` |
| `PROVIDER_BASE_URL` | `https://jsonplaceholder.typicode.com` | Base URL do provider |
| `HTTP_TIMEOUT` | `5` | Timeout (segundos) das chamadas externas |
| `MAX_USER_IDS` | `500` | Máximo de IDs por requisição |
| `CACHE_BACKEND` | `postgres` | Cache: `postgres` ou `memory` |
| `CACHE_TTL_SECONDS` | `300` | TTL do cache de usuários |
| `CACHE_JITTER_SECONDS` | `30` | Jitter somado ao TTL (evita expiração em massa) |
| `CORS_ORIGINS` | `["http://localhost:5173"]` | Origens permitidas (JSON ou separadas por vírgula) |

### Frontend (`frontend/.env`, veja `frontend/.env.example`)

| Variável | Padrão | Descrição |
| --- | --- | --- |
| `VITE_API_BASE_URL` | *(vazio)* | URL base do backend. Vazio = mesma origem (usa o proxy `/api` em dev). |
| `VITE_USER_PROVIDER_URL` | `https://jsonplaceholder.typicode.com/users` | Base usada no link “abrir no provider” dos cards. |
| `VITE_MAX_USER_IDS` | `500` | Limite de IDs validado no cliente (deve bater com `MAX_USER_IDS` do backend). |

---

## Decisões técnicas

### Backend

- **Provider abstraído por `Protocol`.** `UserService` conhece apenas a interface
  `fetch_user(id)`. Trocar o JSONPlaceholder por outra API (ou por um fake) é só configurar
  `USER_PROVIDER`, sem reescrever a regra de negócio.
- **Assíncrono com isolamento de falhas.** Cada ID é consultado em paralelo via
  `asyncio.gather(..., return_exceptions=True)`; exceções individuais viram `failed` e não
  derrubam o lote.
- **Tratamento de erros externos no provider.** `404 → UserNotFoundError`;
  timeout/erros de transporte/HTTP ≥ 400 ou resposta inválida → `ProviderError`.
- **Motivo das falhas explícito.** Além de `failed`, a resposta traz `errors: [{id, reason}]`
  distinguindo `not_found` de `provider_error`.
- **`GET /users/{id}` por ID** (em vez de o provider de lista `/users`): atende diretamente o
  requisito de consultas assíncronas independentes e de isolamento por usuário.
- **Validação na borda com Pydantic.** A entrada é validada antes de chegar ao service e o
  contrato de saída é explícito (`response_model`).
- **Configuração tipada** com pydantic-settings: `DATABASE_URL` obrigatória, timeouts/limites
  positivos e CORS aceitando JSON ou lista separada por vírgula.
- **Cache-aside no PostgreSQL.** Os IDs são buscados no cache (`users`) antes do provider;
  só os *miss* vão à API externa e, no sucesso, são gravados com TTL (+ jitter). Falhas não
  são cacheadas. O cache é **plugável** (`CACHE_BACKEND=postgres|memory`) e as operações são
  *best-effort*: se o cache falhar, a resposta cai para o provider e o erro é logado.
- **Migrations com Alembic.** Schema versionado; o entrypoint do Docker aplica
  `alembic upgrade head` (com retry) antes de subir a API.
- **Observabilidade.** Logging estruturado (structlog/JSON) com `request_id` propagado por
  middleware e devolvido no header `x-request-id`; o service loga `cache_hits`, `cache_misses`,
  `success`, `failed` e `duration_ms`.
- **Camadas finas:** rota → service → provider. Rotas não contêm regra de negócio.

### Frontend

- **Proxy de desenvolvimento.** O Vite encaminha `/api` para `http://localhost:8000`,
  evitando CORS; `VITE_API_BASE_URL` sobrescreve para produção.
- **Contrato isolado em `api/userApi.ts`.** Respostas não-2xx (incluindo o `detail` do
  FastAPI) e falhas de rede viram `ApiError`, mantendo a UI simples.
- **Validação na borda.** O parse aceita IDs separados por vírgula/espaço/quebra de linha,
  rejeita valores não inteiros/não positivos, deduplica preservando a ordem e aplica o limite
  antes de chamar o backend.
- **Estado explícito** (`idle → loading → success | error`), com botão desabilitado durante a
  consulta e erro do backend separado do erro de validação local.
- **Performance em listas grandes.** `UserCard` é `React.memo`, os cards usam
  `content-visibility: auto` e as listas paginam por clique (“Mostrar mais”).
- **Sem biblioteca de UI.** CSS puro (CSS Modules), layout simples e responsivo.

---

## Testes

### Backend

```bash
cd backend
uv run pytest                    # unit (sem rede/DB)
uv run pytest -m integration     # requer DATABASE_URL (Postgres)
```

Os testes **não dependem de rede**: `FakeUserProvider` e `InMemoryUserCache` são injetados via
`dependency_overrides`, e o provider HTTP é testado com `httpx.MockTransport`.

Cobertura (13 testes + 1 de integração):

1. **Consulta com sucesso** — todos os IDs encontrados; `failed`/`errors` vazios.
2. **Falha parcial** — um ID não encontrado não interrompe os demais; vai para `failed` e
   `errors` com `reason="not_found"`.
3. **Cache hit** — a segunda consulta dos mesmos IDs não chama o provider.
4. **Deduplicação** de IDs repetidos.
5. **Validação** de payload (`[]`, IDs não positivos, body ausente) → `422`.
6. **Provider** — sucesso, `404 → not_found`, `3xx/4xx/5xx → provider_error`, JSON inválido e
   payload inesperado → `provider_error`.
7. **Integração (Postgres)** — `upsert`, leitura por `expires_at` e `delete_expired`
   (roda no CI com Postgres; *skip* sem `DATABASE_URL`).

### Frontend

```bash
cd frontend
yarn typecheck     # tsc --noEmit (strict)
yarn build         # typecheck + build de produção
```

### Qualidade e CI

```bash
cd backend
uv run ruff check . && uv run mypy app
```

O CI (GitHub Actions, `.github/workflows/ci.yml`) sobe um Postgres de serviço, aplica as
migrations e roda `ruff`, `mypy` e `pytest` (unit + integração).

---

## O que melhoraria com mais tempo

**Backend**

- **Concorrência limitada** (semáforo) e **retry com backoff/429** para resiliência sob carga.
- **Histórico/auditoria** das consultas em tabela própria (além do cache).
- **Negative cache** curto para `not_found` e *single-flight* contra stampede.
- **Endpoint em lote** no provider (`/users`) como alternativa ao modelo 1-por-ID.
- **Métricas** (latência/taxa de erro), tracing e circuit breaker para o provider.

**Frontend**

- **Testes automatizados** (Vitest + React Testing Library) e **E2E** (Playwright).
- **Docker/CI do frontend** (build + preview) e deploy estático.
- **Paginação/virtualização** para bases muito grandes e acessibilidade (a11y) revisada.
- Exibir o **motivo** de cada falha (`errors[].reason`) e internacionalização (i18n).

**Projeto**

- Cache distribuído (Redis) e rate limiting na borda.

---

## Uso de IA

**OpenCode** (assistente de código no terminal) para: estruturar o projeto e os
diretórios, gerar o boilerplate inicial, revisar/refatorar o código, implementar o cache no
PostgreSQL e a interface React, e redigir a documentação. As decisões de arquitetura, o
desenho do endpoint e a validação do comportamento foram feitos e conferidos manualmente.

---

## E se precisasse consultar milhares de usuários?

O gargalo atual é o modelo **1 requisição HTTP por ID**, sem limite de concorrência. Para
milhares de IDs eu mudaria:

1. **Endpoint em lote no provider.** Trocaria N chamadas por uma consulta a `/users`
   (ou um endpoint bulk), montando um mapa `id → user` e resolvendo tudo em 1 ida à rede.
2. **Concorrência limitada + retry.** Um semáforo para limitar chamadas simultâneas e retry
   com backoff exponencial + jitter, respeitando `Retry-After` em HTTP 429.
3. **Processamento fora do request.** Para volumes grandes, enfileirar o trabalho
   (ex.: Redis + ARQ/Celery), responder com um `job_id` e expor o resultado por polling ou
   webhook — evitando request de vários segundos.
4. **Cache/DB.** O cache de usuários com TTL já existe no PostgreSQL; para volumes maiores,
   trocaria por Redis (compartilhado entre instâncias) e persistiria histórico das execuções.
5. **Paginação/batching interno.** Processar os IDs em lotes menores, com controle de
   pressão (backpressure) e timeouts por lote.
6. **Observabilidade e resiliência.** Métricas (latência, taxa de erro), logs estruturados,
   circuit breaker para o provider e timeout global do request.
7. **Escala horizontal.** API stateless atrás de um load balancer, múltiplos workers
   Uvicorn e pool de conexões dimensionado.

Na prática, a combinação **bulk endpoint + cache + fila para lotes muito grandes** torna o
custo próximo de O(1) em chamadas de rede por requisição, independente do número de IDs.

---
