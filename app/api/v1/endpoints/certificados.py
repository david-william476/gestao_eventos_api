from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.security import exigir_perfis
from app.database.session import get_session
from app.models.models import Certificado, Inscricao, PerfilUsuario, StatusInscricao
from app.schemas.schemas import CertificadoCriacao

router = APIRouter()


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def emitir_certificado(
    dados: CertificadoCriacao,
    session: Session = Depends(get_session),
    usuario_atual=Depends(exigir_perfis(PerfilUsuario.ADMIN, PerfilUsuario.ORGANIZADOR)),
):
    inscricao = session.get(Inscricao, dados.inscricao_id)
    if not inscricao:
        raise HTTPException(status_code=404, detail="A inscrição informada não existe.")

    if inscricao.status != StatusInscricao.ATIVA:
        raise HTTPException(status_code=400, detail="Não é possível emitir certificado para inscrições canceladas.")

    if usuario_atual.perfil == PerfilUsuario.ORGANIZADOR and inscricao.evento.organizador_id != usuario_atual.id:
        raise HTTPException(status_code=403, detail="Você não pode emitir certificado para este evento.")

    certificado_existente = session.exec(
        select(Certificado).where(Certificado.inscricao_id == dados.inscricao_id)
    ).first()
    if certificado_existente:
        raise HTTPException(status_code=400, detail="O certificado para esta inscrição já foi emitido.")

    certificado = Certificado(inscricao_id=dados.inscricao_id)
    session.add(certificado)
    session.commit()
    session.refresh(certificado)
    return {
        "sucesso": True,
        "mensagem": "Certificado emitido com sucesso.",
        "dados": {
            "id": certificado.id,
            "inscricao_id": certificado.inscricao_id,
            "data_emissao": str(certificado.data_emissao),
        },
    }
