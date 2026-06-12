import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from vpo import router as vpo_router
import os
import httpx
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicializa o cliente HTTP global para ser reutilizado
    async with httpx.AsyncClient() as client:
        app.state.http_client = client
        yield
    # O cliente é fechado automaticamente ao sair do bloco contextmanager

app = FastAPI(title="Sistema VPO Monsanto - Velozter", lifespan=lifespan)

# Inclui as rotas da API
app.include_router(vpo_router)

@app.get("/")
async def root():
    """Serve a página inicial do transportador."""
    return FileResponse("templates/index.html")

@app.get("/health")
async def health():
    """Endpoint de verificação de saúde para o Render/UptimeRobot."""
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)