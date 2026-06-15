import json
import httpx
import os
import logging
import asyncio
from typing import Any, Dict
from dclogg_auth import get_token

logger = logging.getLogger(__name__)

async def executar_compra(payload: Dict[str, Any], client: httpx.AsyncClient, request_id: str) -> Dict[str, Any]:
    token = await get_token(client, request_id)
    url = os.getenv("PURCHASE_API_URL")
    if not url:
        raise ValueError("A variável de ambiente PURCHASE_API_URL não foi configurada.")

    headers: Dict[str, str] = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # Serialização estrita: Remove espaços extras que causam 'Policy Falsified'
    payload_json = json.dumps(payload, separators=(',', ':'))

    # Implementação de Resiliência: Retry Loop
    max_tentativas = 3
    for tentativa in range(max_tentativas):
        try:
            logger.info(f"[{request_id}] Tentativa {tentativa + 1} de envio para DCLOGG...")
            response = await client.post(
                url,
                content=payload_json,
                headers=headers
            )
            
            if response.status_code == 200:
                logger.info(f"[{request_id}] Compra realizada com sucesso.")
                return {"status": "success", "data": response.json(), "request_id": request_id}
            
            logger.error(f"[{request_id}] API retornou erro ({response.status_code}): {response.text}")
            if tentativa == max_tentativas - 1:
                return {"status": "error", "code": response.status_code, "message": response.text, "request_id": request_id}

        except (httpx.TimeoutException, httpx.NetworkError) as e:
            logger.warning(f"[{request_id}] Falha de rede/timeout na tentativa {tentativa + 1}: {str(e)}")
            if tentativa == max_tentativas - 1:
                raise e
            await asyncio.sleep(1.5 * (tentativa + 1)) # Backoff exponencial simples
            
    return {"status": "error", "message": "Falha após múltiplas tentativas", "request_id": request_id}