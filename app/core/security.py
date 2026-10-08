import base64
import hashlib
import hmac
import json
import os
import time

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session

from app.database.session import get_session
from app.models.models import Usuario, PerfilUsuario

SECRET_KEY = os.getenv("API_SECRET_KEY", "chave-secreta-api-eventos-mvp-2026")
ALGORITHM = "HS256"
TOKEN_EXPIRE_SECONDS = 60 * 60 * 8
security = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    derived = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 120_000)
    return f"pbkdf2_sha256$120000${base64.urlsafe_b64encode(salt).decode()}${base64.urlsafe_b64encode(derived).decode()}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, iterations, salt_b64, hash_b64 = stored_hash.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return hmac.compare_digest(password, stored_hash)
        salt = base64.urlsafe_b64decode(salt_b64.encode())
        expected = base64.urlsafe_b64decode(hash_b64.encode())
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, int(iterations))
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return hmac.compare_digest(password, stored_hash)


def create_access_token(usuario: Usuario) -> str:
    payload = {
        "sub": usuario.id,
        "perfil": usuario.perfil.value if isinstance(usuario.perfil, PerfilUsuario) else str(usuario.perfil),
        "exp": int(time.time()) + TOKEN_EXPIRE_SECONDS,
    }
    payload_bytes = json.dumps(payload, separators=(",", ":")).encode()
    payload_b64 = base64.urlsafe_b64encode(payload_bytes).decode().rstrip("=")
    signature = hmac.new(SECRET_KEY.encode(), payload_b64.encode(), hashlib.sha256).digest()
    signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip("=")
    return f"{payload_b64}.{signature_b64}"


def _decode_token(token: str) -> dict:
    try:
        payload_b64, signature_b64 = token.split(".", 1)
        expected_signature = hmac.new(SECRET_KEY.encode(), payload_b64.encode(), hashlib.sha256).digest()
        received_signature = base64.urlsafe_b64decode(signature_b64 + "===")
        if not hmac.compare_digest(expected_signature, received_signature):
            raise ValueError("assinatura inválida")
        payload = json.loads(base64.urlsafe_b64decode(payload_b64 + "===").decode())
        if int(payload.get("exp", 0)) < int(time.time()):
            raise ValueError("token expirado")
        return payload
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado. Faça login novamente.",
        ) from exc


def get_usuario_atual(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session),
) -> Usuario:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="É necessário informar um token Bearer.",
        )

    payload = _decode_token(credentials.credentials)
    usuario = session.get(Usuario, int(payload["sub"]))
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuário do token não encontrado.")
    return usuario


def exigir_perfis(*perfis_permitidos: PerfilUsuario):
    def dependency(usuario: Usuario = Depends(get_usuario_atual)) -> Usuario:
        if usuario.perfil not in perfis_permitidos:
            nomes = ", ".join(perfil.value for perfil in perfis_permitidos)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso permitido somente para: {nomes}.",
            )
        return usuario

    return dependency
