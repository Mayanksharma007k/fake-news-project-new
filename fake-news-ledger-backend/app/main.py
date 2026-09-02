from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.routes.verification import router as verification_router
from app.routes.ledger import router as ledger_router

app=FastAPI(title="Fake News Ledger API",version="1.0.0",
            description="AI evidence assessment with tamper-evident verification records.")

app.add_middleware(CORSMiddleware,allow_origins=["http://localhost:3000"],
                   allow_credentials=True,allow_methods=["*"],allow_headers=["*"])

@app.on_event("startup")
async def startup():
    await init_db()

@app.get("/health")
async def health():
    return {"status":"ok","service":"fake-news-ledger"}

app.include_router(verification_router)
app.include_router(ledger_router)
