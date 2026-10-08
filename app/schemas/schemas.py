from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.models.models import PerfilUsuario, StatusEvento, StatusInscricao


class UsuarioCriacao(BaseModel):
    nome: str = Field(min_length=2)
    email: EmailStr
    senha: str = Field(min_length=6)
    perfil: PerfilUsuario


class LoginRequest(BaseModel):
    email: EmailStr
    senha: str


class UsuarioResposta(BaseModel):
    id: int
    nome: str
    email: EmailStr
    perfil: PerfilUsuario


class EventoCriacao(BaseModel):
    titulo: str = Field(min_length=2)
    descricao: Optional[str] = None
    data_evento: str
    capacidade: int = Field(gt=0)
    status: StatusEvento = StatusEvento.ATIVO
    organizador_id: Optional[int] = None
    categoria_id: int


class EventoAtualizacao(BaseModel):
    titulo: Optional[str] = Field(default=None, min_length=2)
    descricao: Optional[str] = None
    data_evento: Optional[str] = None
    capacidade: Optional[int] = Field(default=None, gt=0)
    status: Optional[StatusEvento] = None
    categoria_id: Optional[int] = None


class InscricaoCriacao(BaseModel):
    evento_id: int
    usuario_id: Optional[int] = None


class CertificadoCriacao(BaseModel):
    inscricao_id: int
