from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.security import exigir_perfis, get_usuario_atual
from app.database.session import get_session
from app.models.models import Categoria, Evento, Inscricao, PerfilUsuario, StatusEvento
from app.schemas.schemas import EventoAtualizacao, EventoCriacao

router = APIRouter()


def validar_data(data_evento: str):
    try:
        data_convertida = datetime.strptime(data_evento, "%Y-%m-%d").date()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de data inválido. Use o padrão AAAA-MM-DD.",
        ) from exc

    if data_convertida < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é permitido cadastrar ou agendar um evento com data passada.",
        )


def dados_evento(evento: Evento):
    return {
        "id": evento.id,
        "titulo": evento.titulo,
        "descricao": evento.descricao,
        "data_evento": evento.data_evento,
        "capacidade": evento.capacidade,
        "status": evento.status,
        "organizador_id": evento.organizador_id,
        "categoria_id": evento.categoria_id,
    }


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def criar_evento(
    evento: EventoCriacao,
    session: Session = Depends(get_session),
    usuario_atual=Depends(exigir_perfis(PerfilUsuario.ADMIN, PerfilUsuario.ORGANIZADOR)),
):
    validar_data(evento.data_evento)

    categoria = session.get(Categoria, evento.categoria_id)
    if not categoria:
        raise HTTPException(status_code=404, detail="A categoria informada não existe no sistema.")

    organizador_id = usuario_atual.id
    if usuario_atual.perfil == PerfilUsuario.ADMIN and evento.organizador_id:
        organizador = session.get(type(usuario_atual), evento.organizador_id)
        if not organizador:
            raise HTTPException(status_code=404, detail="O organizador informado não existe.")
        organizador_id = organizador.id

    novo_evento = Evento(
        titulo=evento.titulo,
        descricao=evento.descricao,
        data_evento=evento.data_evento,
        capacidade=evento.capacidade,
        status=evento.status,
        organizador_id=organizador_id,
        categoria_id=evento.categoria_id,
    )
    session.add(novo_evento)
    session.commit()
    session.refresh(novo_evento)

    return {"sucesso": True, "mensagem": "Evento criado com sucesso.", "dados": dados_evento(novo_evento)}


@router.get("/", response_model=dict)
def listar_eventos(session: Session = Depends(get_session)):
    eventos = session.exec(select(Evento)).all()
    return {
        "sucesso": True,
        "mensagem": "Consulta realizada com sucesso.",
        "dados": [dados_evento(e) for e in eventos],
    }


@router.get("/{evento_id}", response_model=dict)
def buscar_evento(evento_id: int, session: Session = Depends(get_session)):
    evento = session.get(Evento, evento_id)
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado.")
    return {"sucesso": True, "mensagem": "Evento encontrado com sucesso.", "dados": dados_evento(evento)}


@router.put("/{evento_id}", response_model=dict)
def atualizar_evento(
    evento_id: int,
    dados: EventoAtualizacao,
    session: Session = Depends(get_session),
    usuario_atual=Depends(get_usuario_atual),
):
    evento = session.get(Evento, evento_id)
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado.")

    if usuario_atual.perfil != PerfilUsuario.ADMIN and evento.organizador_id != usuario_atual.id:
        raise HTTPException(status_code=403, detail="Você não tem permissão para editar este evento.")

    atualizacoes = dados.model_dump(exclude_unset=True)
    if "data_evento" in atualizacoes:
        validar_data(atualizacoes["data_evento"])
    if "categoria_id" in atualizacoes:
        if not session.get(Categoria, atualizacoes["categoria_id"]):
            raise HTTPException(status_code=404, detail="A categoria informada não existe no sistema.")

    for campo, valor in atualizacoes.items():
        setattr(evento, campo, valor)

    session.add(evento)
    session.commit()
    session.refresh(evento)
    return {"sucesso": True, "mensagem": "Evento atualizado com sucesso.", "dados": dados_evento(evento)}


@router.delete("/{evento_id}", response_model=dict, status_code=status.HTTP_200_OK)
def excluir_evento(
    evento_id: int,
    session: Session = Depends(get_session),
    usuario_atual=Depends(get_usuario_atual),
):
    evento = session.get(Evento, evento_id)
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado.")

    if usuario_atual.perfil != PerfilUsuario.ADMIN and evento.organizador_id != usuario_atual.id:
        raise HTTPException(status_code=403, detail="Você não tem permissão para excluir este evento.")

    inscricoes = session.exec(select(Inscricao).where(Inscricao.evento_id == evento_id)).all()
    for inscricao in inscricoes:
        if inscricao.certificado:
            session.delete(inscricao.certificado)
        session.delete(inscricao)

    session.delete(evento)
    session.commit()
    return {"sucesso": True, "mensagem": "Evento excluído com sucesso.", "dados": None}


@router.get("/{evento_id}/inscritos", response_model=dict)
def listar_inscritos(
    evento_id: int,
    session: Session = Depends(get_session),
    usuario_atual=Depends(get_usuario_atual),
):
    evento = session.get(Evento, evento_id)
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado.")

    if usuario_atual.perfil != PerfilUsuario.ADMIN and evento.organizador_id != usuario_atual.id:
        raise HTTPException(status_code=403, detail="Você não tem permissão para consultar os inscritos deste evento.")

    inscricoes = session.exec(select(Inscricao).where(Inscricao.evento_id == evento_id)).all()
    dados = [
        {
            "inscricao_id": i.id,
            "usuario_id": i.usuario_id,
            "nome": i.usuario.nome if i.usuario else None,
            "email": i.usuario.email if i.usuario else None,
            "status": i.status,
            "data_inscricao": str(i.data_inscricao),
        }
        for i in inscricoes
    ]
    return {"sucesso": True, "mensagem": "Lista de inscritos consultada com sucesso.", "dados": dados}
