import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.responses import FileResponse
from vpo import router as vpo_router
import os
import httpx
import uuid
from contextlib import asynccontextmanager
from typing import Any, Callable, Dict

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Configuração Enterprise: Timeout global e reuso de conexões
    limits = httpx.Limits(max_connections=100, max_keepalive_connections=20)
    timeout = httpx.Timeout(30.0, connect=10.0)
    
    async with httpx.AsyncClient(limits=limits, timeout=timeout) as client:
        app.state.http_client = client
        yield

app = FastAPI(title="Sistema VPO Monsanto - Velozter", lifespan=lifespan)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next: Callable[[Request], Any]) -> Response:
    # Gera um ID de transação único por requisição para rastreabilidade
    request.state.request_id = str(uuid.uuid4())
    response: Response = await call_next(request)
    response.headers["X-Request-ID"] = request.state.request_id
    return response

# Inclui as rotas da API
app.include_router(vpo_router)

@app.get("/")
async def root() -> FileResponse:
    """Serve a página inicial do transportador."""
    return FileResponse("templates/index.html")

@app.get("/health")
async def health() -> Dict[str, str]:
    """Endpoint de verificação de saúde para o Render/UptimeRobot."""
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)