import uvicorn
from fastapi import FastAPI

from app.api.v1.endpoints import auth, categorias, certificados, eventos, inscricoes, usuarios
from app.database.session import criar_banco_e_tabelas

app = FastAPI(
    title="Sistema de Gestão de Eventos Acadêmicos",
    description="API para gerenciamento de usuários, eventos, inscrições e certificados.",
    version="2.0.0",
)


@app.on_event("startup")
def on_startup():
    criar_banco_e_tabelas()


app.include_router(auth.router, prefix="/api/v1/auth", tags=["Autenticação"])
app.include_router(usuarios.router, prefix="/api/v1/usuarios", tags=["Usuários"])
app.include_router(categorias.router, prefix="/api/v1/categorias", tags=["Categorias"])
app.include_router(eventos.router, prefix="/api/v1/eventos", tags=["Eventos"])
app.include_router(inscricoes.router, prefix="/api/v1/inscricoes", tags=["Inscrições"])
app.include_router(certificados.router, prefix="/api/v1/certificados", tags=["Certificados"])


@app.get("/", tags=["Home"])
def read_root():
    return {"status": "API Online", "docs": "/docs"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
