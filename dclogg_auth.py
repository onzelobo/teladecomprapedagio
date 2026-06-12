import os
import time
import httpx
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

_cached_token = None
_expires_at = 0

async def get_token():
    global _cached_token, _expires_at

    # Se o token existir e faltar mais de 1 minuto para expirar, reutiliza
    if _cached_token and time.time() < (_expires_at - 60):
        return _cached_token

    url = os.getenv("AUTH_API_URL")
    data = {
        "client_id": os.getenv("CLIENT_ID"),
        "client_secret": os.getenv("CLIENT_SECRET"),
        "grant_type": "client_credentials",
        "scope": "dclogg-internal"
    }

    async with httpx.AsyncClient() as client:
        logger.info("Solicitando novo token de acesso OAuth2...")
        response = await client.post(url, data=data, timeout=10)
        
        if response.status_code != 200:
            logger.error(f"Falha na autenticação: {response.text}")
            raise RuntimeError("Não foi possível autenticar com o provedor de Vale Pedágio.")
            
        res_data = response.json()
        _cached_token = res_data["access_token"]
        # Define expiração baseada no tempo atual + segundos informados
        _expires_at = time.time() + res_data.get("expires_in", 1800)
        
        return _cached_token