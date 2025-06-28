import asyncio
import uvicorn
from fastapi import FastAPI
from charger_manager.ws_server import start_websocket_server
from api.endpoints import router as api_router

app = FastAPI()
app.include_router(api_router)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(start_websocket_server())

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
