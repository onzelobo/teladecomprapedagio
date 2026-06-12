from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from os_transform import gerar_dt
from payload_builder import build_payload
from dclogg_compra import executar_compra
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/vpo", tags=["Vale Pedágio"])

class Localizacao(BaseModel):
    cidade: str = Field(..., example="SAO PAULO")
    uf: str = Field(..., min_length=2, max_length=2, example="SP")

class CompraRequest(BaseModel):
    placa: str = Field(..., example="ABC1234")
    os: str = Field(..., example="4SSA128276A")
    eixos: int = Field(..., gt=0, example=3)
    origem: Localizacao
    destino: Localizacao

@router.post("/comprar")
async def comprar_vpo(request: Request, compra_data: CompraRequest):
    try:
        # 1. Transformação OS -> DT
        dt = gerar_dt(compra_data.os)
        
        # 2. Construção do payload
        dados = compra_data.model_dump()
        dados["dt"] = dt
        payload = build_payload(dados)
        
        # 3. Execução da integração
        # Passamos o cliente HTTP que está no estado do app
        resultado = await executar_compra(payload, request.app.state.http_client)
        return resultado

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Erro não tratado na compra de VPO")
        raise HTTPException(status_code=500, detail="Erro interno no servidor ao processar a compra.")