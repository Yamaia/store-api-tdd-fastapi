# Store API — FastAPI + MongoDB com TDD

API de produtos construída com **Test Driven Development**, como projeto prático do bootcamp da DIO.
Baseada em [digitalinnovationone/store_api](https://github.com/digitalinnovationone/store_api), incluindo o **desafio final** e melhorias.

## Stack

FastAPI · MongoDB (Motor) · Pydantic v2 · Pytest · pytest-asyncio · httpx · mongomock-motor · Poetry · Docker · GitHub Actions

## Estrutura

```
store/
├── core/         # configurações e exceções
├── db/           # conexão com o MongoDB
├── schemas/      # validação (Pydantic)
├── usecases/     # regras de negócio e acesso ao banco
├── controllers/  # rotas e tratamento de exceções → HTTP
└── main.py
tests/            # schemas, usecases e controllers (integração)
```

## Endpoints

| Método | Rota             | Sucesso | Erros        |
| ------ | ---------------- | ------- | ------------ |
| POST   | `/products`      | 201     | 422, 500     |
| GET    | `/products`      | 200     | 422          |
| GET    | `/products/{id}` | 200     | 404          |
| PATCH  | `/products/{id}` | 200     | 404, 422     |
| DELETE | `/products/{id}` | 204     | 404          |

Filtro de preço (`price > 5000 and price < 8000`) e paginação:

```
GET /products?price_gt=5000&price_lt=8000&limit=20&offset=0
```

## Desafio final — o que foi feito

- **Create:** falha de inserção vira `InsertionException` e a controller responde **500** com mensagem amigável.
- **Update:**
  - `PATCH` lança `NotFoundException` quando o produto não existe, e a controller responde **404** com mensagem amigável.
  - `updated_at` é preenchido com o horário atual a cada alteração, mas pode ser enviado manualmente no corpo.
- **Filtros:** produtos com preços diferentes e filtro `price_gt` / `price_lt` (limites **exclusivos**, conforme o enunciado).

## Melhorias além do desafio

- Preço salvo em **centavos (inteiro)** no banco: exato e comparável nos filtros; a API expõe `Decimal` com 2 casas.
- Paginação (`limit`/`offset`) e validação de intervalo de preço (`price_gt < price_lt`).
- Testes sem depender de um Mongo rodando (`mongomock-motor` + override de dependência).
- CI com GitHub Actions, `Dockerfile` e `docker-compose`.

## Como rodar

```bash
cp .env.example .env
poetry install
docker compose up -d mongo
poetry run uvicorn store.main:app --reload
```

Documentação interativa: http://localhost:8000/docs

## Testes

```bash
poetry run pytest -v
poetry run pytest --cov=store --cov-report=term-missing
```

O ciclo seguido: **escrever o teste (falha) → implementar (passa) → refatorar**.

## Autor

Desenvolvido por Yamaia — desenvolvedor backend (Python · FastAPI · Azure).
