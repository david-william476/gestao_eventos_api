# Sistema de Gestão de Eventos Acadêmicos - API

API REST feita com FastAPI + SQLModel + SQLite.

## Instalação

No terminal, dentro da pasta do projeto:

```powershell
python -m pip install -r requirements.txt
```

## Executar

```powershell
python -m uvicorn main:app --reload
```

Swagger:

`http://127.0.0.1:8000/docs`

## Fluxo recomendado para testar

1. Criar uma categoria.
2. Criar um usuário com perfil `admin` ou `organizador`.
3. Fazer login em `POST /api/v1/auth/login`.
4. Copiar o `access_token`.
5. No Swagger, clicar em **Authorize** e informar `Bearer SEU_TOKEN`.
6. Criar um evento.
7. Criar um usuário `participante`.
8. Fazer login com o participante.
9. Criar uma inscrição.
10. Testar o cancelamento da inscrição com `DELETE /api/v1/inscricoes/{id}`.
11. Testar consulta, edição e exclusão do evento.
12. Testar a emissão de certificado para uma inscrição ativa.

## Rotas principais

- POST `/api/v1/usuarios`
- POST `/api/v1/auth/login`
- POST `/api/v1/eventos`
- GET `/api/v1/eventos`
- GET `/api/v1/eventos/{id}`
- PUT `/api/v1/eventos/{id}`
- DELETE `/api/v1/eventos/{id}`
- POST `/api/v1/inscricoes`
- DELETE `/api/v1/inscricoes/{id}`
- GET `/api/v1/eventos/{id}/inscritos`
- POST `/api/v1/certificados`

Também existem as rotas de categorias e listagem de usuários.
