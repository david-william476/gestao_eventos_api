from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.security import create_access_token, verify_password
from app.database.session import get_session
from app.models.models import Usuario
from app.schemas.schemas import LoginRequest

router = APIRouter()


@router.post("/login", response_model=dict)
def login(dados: LoginRequest, session: Session = Depends(get_session)):
    usuario = session.exec(select(Usuario).where(Usuario.email == dados.email)).first()

    if not usuario or not verify_password(dados.senha, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos.",
        )

    token = create_access_token(usuario)
    return {
        "sucesso": True,
        "mensagem": "Login realizado com sucesso.",
        "dados": {
            "access_token": token,
            "token_type": "bearer",
            "usuario": {
                "id": usuario.id,
                "nome": usuario.nome,
                "email": usuario.email,
                "perfil": usuario.perfil,
            },
        },
    }
