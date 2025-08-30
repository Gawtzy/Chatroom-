from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import auth_router, frontend, websocket_router

app = FastAPI(title="Distributed Chat API")

app.include_router(frontend)

app.include_router(websocket_router)

app.include_router(auth_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)