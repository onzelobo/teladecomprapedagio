import os
import time
import httpx
import logging
from typing import Any, Dict, Optional
from dotenv import load_dotenv

# Carrega .env apenas se o arquivo existir (desenvolvimento local)
if os.path.exists(".env"):
    load_dotenv()

logger = logging.getLogger(__name__)

_cached_token: Optional[str] = None
_expires_at: float = 0

async def get_token(client: httpx.AsyncClient, request_id: str = "internal") -> str:
    global _cached_token, _expires_at

    # Se o token existir e faltar mais de 1 minuto para expirar, reutiliza
    if _cached_token and time.time() < (_expires_at - 60):
        return _cached_token

    url = os.getenv("AUTH_API_URL")
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")

    if not all([url, client_id, client_secret]):
        raise ValueError("Configurações de autenticação (URL, ID ou Secret) ausentes nas variáveis de ambiente.")

    data: Dict[str, str] = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
        "scope": "dclogg-internal"
    }

    logger.info(f"[{request_id}] Solicitando novo token de acesso OAuth2...")
    response = await client.post(url, data=data, timeout=10)
    
    if response.status_code != 200:
        logger.error(f"[{request_id}] Falha na autenticação: {response.text}")
        raise RuntimeError("Não foi possível autenticar com o provedor de Vale Pedágio.")
        
    res_data: Dict[str, Any] = response.json()
    access_token = res_data.get("access_token")

    if not isinstance(access_token, str):
        raise RuntimeError("Token de acesso não encontrado ou inválido na resposta da API.")

    _cached_token = access_token
    # Define expiração baseada no tempo atual + segundos informados
    _expires_at = time.time() + res_data.get("expires_in", 1800)
    
    return access_token