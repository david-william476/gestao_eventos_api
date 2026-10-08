from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.security import get_usuario_atual
from app.database.session import get_session
from app.models.models import Evento, Inscricao, StatusEvento, StatusInscricao, Usuario
from app.schemas.schemas import InscricaoCriacao

router = APIRouter()


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def realizar_inscricao(
    inscricao: InscricaoCriacao,
    session: Session = Depends(get_session),
    usuario_atual=Depends(get_usuario_atual),
):
    evento = session.get(Evento, inscricao.evento_id)
    if not evento:
        raise HTTPException(status_code=404, detail="O evento informado não existe.")

    usuario_id = usuario_atual.id
    if inscricao.usuario_id is not None:
        if usuario_atual.perfil.value == "admin":
            usuario_id = inscricao.usuario_id
        elif inscricao.usuario_id != usuario_atual.id:
            raise HTTPException(status_code=403, detail="Você só pode realizar inscrição para o próprio usuário.")

    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="O usuário informado não existe.")

    if evento.status != StatusEvento.ATIVO:
        raise HTTPException(status_code=400, detail="Não é possível se inscrever em um evento cancelado ou encerrado.")

    inscricao_existente = session.exec(
        select(Inscricao).where(
            Inscricao.usuario_id == usuario_id,
            Inscricao.evento_id == inscricao.evento_id,
        )
    ).first()
    if inscricao_existente and inscricao_existente.status == StatusInscricao.ATIVA:
        raise HTTPException(status_code=400, detail="O usuário já está inscrito neste evento.")

    total_inscritos = len(
        session.exec(
            select(Inscricao).where(
                Inscricao.evento_id == inscricao.evento_id,
                Inscricao.status == StatusInscricao.ATIVA,
            )
        ).all()
    )
    if total_inscritos >= evento.capacidade:
        raise HTTPException(status_code=400, detail="A capacidade máxima deste evento já foi esgotada.")

    if inscricao_existente:
        inscricao_existente.status = StatusInscricao.ATIVA
        session.add(inscricao_existente)
        session.commit()
        session.refresh(inscricao_existente)
        nova_inscricao = inscricao_existente
    else:
        nova_inscricao = Inscricao(
            usuario_id=usuario_id,
            evento_id=inscricao.evento_id,
            status=StatusInscricao.ATIVA,
        )
        session.add(nova_inscricao)
        session.commit()
        session.refresh(nova_inscricao)

    return {
        "sucesso": True,
        "mensagem": "Inscrição realizada com sucesso.",
        "dados": {
            "id": nova_inscricao.id,
            "usuario_id": nova_inscricao.usuario_id,
            "evento_id": nova_inscricao.evento_id,
            "status": nova_inscricao.status,
        },
    }


@router.delete("/{inscricao_id}", response_model=dict)
def cancelar_inscricao(
    inscricao_id: int,
    session: Session = Depends(get_session),
    usuario_atual=Depends(get_usuario_atual),
):
    inscricao = session.get(Inscricao, inscricao_id)
    if not inscricao:
        raise HTTPException(status_code=404, detail="Inscrição não encontrada.")

    if usuario_atual.perfil.value != "admin" and inscricao.usuario_id != usuario_atual.id:
        raise HTTPException(status_code=403, detail="Você não tem permissão para cancelar esta inscrição.")

    if inscricao.status == StatusInscricao.CANCELADA:
        raise HTTPException(status_code=400, detail="Esta inscrição já está cancelada.")

    inscricao.status = StatusInscricao.CANCELADA
    session.add(inscricao)
    session.commit()
    session.refresh(inscricao)

    return {
        "sucesso": True,
        "mensagem": "Inscrição cancelada com sucesso.",
        "dados": {
            "id": inscricao.id,
            "usuario_id": inscricao.usuario_id,
            "evento_id": inscricao.evento_id,
            "status": inscricao.status,
        },
    }
