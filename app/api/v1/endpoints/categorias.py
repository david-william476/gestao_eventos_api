from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.security import exigir_perfis
from app.database.session import get_session
from app.models.models import Categoria, PerfilUsuario

router = APIRouter()


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def criar_categoria(
    categoria: Categoria,
    session: Session = Depends(get_session),
    usuario_atual=Depends(exigir_perfis(PerfilUsuario.ADMIN)),
):
    categoria_existente = session.exec(select(Categoria).where(Categoria.nome == categoria.nome)).first()
    if categoria_existente:
        raise HTTPException(status_code=400, detail="Uma categoria com este nome já está cadastrada.")
    if len(categoria.nome) < 3:
        raise HTTPException(status_code=400, detail="O nome da categoria deve possuir ao menos 3 caracteres.")
    categoria.id = None
    session.add(categoria)
    session.commit()
    session.refresh(categoria)
    return {"sucesso": True, "mensagem": "Categoria criada com sucesso.", "dados": {"id": categoria.id, "nome": categoria.nome}}


@router.get("/", response_model=dict)
def listar_categorias(session: Session = Depends(get_session)):
    categorias = session.exec(select(Categoria)).all()
    return {"sucesso": True, "mensagem": "Consulta realizada com sucesso.", "dados": [{"id": c.id, "nome": c.nome} for c in categorias]}
