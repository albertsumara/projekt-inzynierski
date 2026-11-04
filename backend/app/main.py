from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.recognition import router as product_router

app = FastAPI(
    title="Diet App",
    description="Diet application manager",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(
    product_router,
    prefix="/api/v1",
    tags=["/product/recognize"],
)
