import json
import httpx
import os
import logging
from dclogg_auth import get_token

logger = logging.getLogger(__name__)

async def executar_compra(payload: dict, client: httpx.AsyncClient):
    token = await get_token(client)
    url = os.getenv("PURCHASE_API_URL")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # Serialização estrita: Remove espaços extras que causam 'Policy Falsified'
    payload_json = json.dumps(payload, separators=(',', ':'))

    logger.info("Enviando requisição de compra para a API...")
    response = await client.post(
        url,
        content=payload_json,
        headers=headers,
        timeout=30.0
    )
    
    if response.status_code != 200:
        logger.error(f"Erro na API ({response.status_code}): {response.text}")
        return {"status": "error", "code": response.status_code, "message": response.text}
        
    logger.info("Compra realizada com sucesso.")
    return {"status": "success", "data": response.json()}