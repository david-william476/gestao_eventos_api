from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.security import hash_password
from app.database.session import get_session
from app.models.models import Usuario
from app.schemas.schemas import UsuarioCriacao

router = APIRouter()


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def cadastrar_usuario(usuario: UsuarioCriacao, session: Session = Depends(get_session)):
    usuario_existente = session.exec(
        select(Usuario).where(Usuario.email == usuario.email)
    ).first()
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O e-mail informado já está cadastrado no sistema.",
        )

    novo_usuario = Usuario(
        nome=usuario.nome,
        email=usuario.email,
        senha_hash=hash_password(usuario.senha),
        perfil=usuario.perfil,
    )
    session.add(novo_usuario)
    session.commit()
    session.refresh(novo_usuario)

    return {
        "sucesso": True,
        "mensagem": "Usuário cadastrado com sucesso.",
        "dados": {
            "id": novo_usuario.id,
            "nome": novo_usuario.nome,
            "email": novo_usuario.email,
            "perfil": novo_usuario.perfil,
        },
    }


@router.get("/", response_model=dict)
def listar_usuarios(session: Session = Depends(get_session)):
    usuarios = session.exec(select(Usuario)).all()
    return {
        "sucesso": True,
        "mensagem": "Consulta realizada com sucesso.",
        "dados": [
            {"id": u.id, "nome": u.nome, "email": u.email, "perfil": u.perfil}
            for u in usuarios
        ],
    }
