from fastapi import APIRouter, HTTPException, Request
from typing import Any, Dict
from pydantic import BaseModel, Field
from os_transform import gerar_dt
from payload_builder import build_payload
from dclogg_compra import executar_compra
import logging
import uuid

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/vpo", tags=["Vale Pedágio"])

class Localizacao(BaseModel):
    cidade: str = Field(..., examples=["SAO PAULO"])
    uf: str = Field(..., min_length=2, max_length=2, examples=["SP"])

class CompraRequest(BaseModel):
    placa: str = Field(..., examples=["ABC1234"])
    os: str = Field(..., examples=["4SSA128276A"])
    eixos: int = Field(..., gt=0, examples=[3])
    origem: Localizacao
    destino: Localizacao

@router.post("/comprar")
async def comprar_vpo(request: Request, compra_data: CompraRequest) -> Dict[str, Any]:
    # Recupera o ID gerado pelo middleware ou gera um novo caso o middleware falhe
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    logger.info(f"[{request_id}] Iniciando processo de compra para placa: {compra_data.placa}")
    
    try:
        # 1. Transformação OS -> DT
        dt = gerar_dt(compra_data.os)
        
        # 2. Construção do payload
        dados = compra_data.model_dump()
        dados["dt"] = dt
        payload = build_payload(dados)
        
        # 3. Execução da integração
        resultado = await executar_compra(payload, request.app.state.http_client, request_id)
        return {
            "request_id": request_id,
            "resultado": resultado
        }

    except ValueError as e:
        logger.warning(f"[{request_id}] Erro de validação: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"[{request_id}] Erro crítico não tratado")
        raise HTTPException(status_code=500, detail="Erro interno no servidor ao processar a compra.")