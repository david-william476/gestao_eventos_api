from datetime import datetime, date
from enum import Enum
from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship


# --- ENUMS REQUISITADOS NA DOCUMENTAÇÃO ---
class PerfilUsuario(str, Enum):
    ADMIN = "admin"
    ORGANIZADOR = "organizador"
    PARTICIPANTE = "participante"


class StatusEvento(str, Enum):
    ATIVO = "ativo"
    CANCELADO = "cancelado"
    ENCERRADO = "encerrado"


class StatusInscricao(str, Enum):
    ATIVA = "ativa"
    CANCELADA = "cancelada"


# --- MODELOS DE TABELAS DO BANCO DE DADOS (SQLModel) ---

class Usuario(SQLModel, table=True):
    __tablename__ = "usuario"

    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str = Field(nullable=False)
    email: str = Field(nullable=False, unique=True)
    senha_hash: str = Field(nullable=False)
    perfil: PerfilUsuario = Field(nullable=False)

    # Relacionamentos (1:N)
    eventos: List["Evento"] = Relationship(back_populates="organizador")
    inscricoes: List["Inscricao"] = Relationship(back_populates="usuario")


class Categoria(SQLModel, table=True):
    __tablename__ = "categoria"

    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str = Field(nullable=False, unique=True)

    # Relacionamento (1:N)
    eventos: List["Evento"] = Relationship(back_populates="categoria")


class Evento(SQLModel, table=True):
    __tablename__ = "evento"

    id: Optional[int] = Field(default=None, primary_key=True)
    titulo: str = Field(nullable=False)
    descricao: Optional[str] = Field(default=None, nullable=True)
    data_evento: str = Field(nullable=False)  # Mantido como str para evitar problemas com SQLite
    capacidade: int = Field(nullable=False)
    status: StatusEvento = Field(default=StatusEvento.ATIVO, nullable=False)

    # Chaves Estrangeiras (FK)
    organizador_id: int = Field(foreign_key="usuario.id", nullable=False)
    categoria_id: int = Field(foreign_key="categoria.id", nullable=False)

    # Relacionamentos Inversos
    organizador: Usuario = Relationship(back_populates="eventos")
    categoria: Categoria = Relationship(back_populates="eventos")
    inscricoes: List["Inscricao"] = Relationship(back_populates="evento")


class Inscricao(SQLModel, table=True):
    __tablename__ = "inscricao"

    id: Optional[int] = Field(default=None, primary_key=True)
    status: StatusInscricao = Field(default=StatusInscricao.ATIVA, nullable=False)
    data_inscricao: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Chaves Estrangeiras (FK)
    usuario_id: int = Field(foreign_key="usuario.id", nullable=False)
    evento_id: int = Field(foreign_key="evento.id", nullable=False)

    # Relacionamentos
    usuario: Usuario = Relationship(back_populates="inscricoes")
    evento: Evento = Relationship(back_populates="inscricoes")
    certificado: Optional["Certificado"] = Relationship(back_populates="inscricao")


class Certificado(SQLModel, table=True):
    __tablename__ = "certificado"

    id: Optional[int] = Field(default=None, primary_key=True)
    data_emissao: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Chave Estrangeira com restrição UNIQUE (Relação 1:1)
    inscricao_id: int = Field(foreign_key="inscricao.id", unique=True, nullable=False)

    # Relacionamento
    inscricao: Inscricao = Relationship(back_populates="certificado")
