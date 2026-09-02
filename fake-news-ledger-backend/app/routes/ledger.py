from fastapi import APIRouter, Depends
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.verification import Verification

router=APIRouter(prefix="/api/ledger",tags=["ledger"])

@router.get("")
async def ledger(db:AsyncSession=Depends(get_db)):
    result=await db.execute(select(Verification).order_by(desc(Verification.created_at)).limit(100))
    rows=result.scalars().all()
    return [{"id":r.id,"claim":r.claim,"status":r.status,"trust_score":r.trust_score,
             "date":r.created_at.isoformat(),"blockchain_verified":bool(r.transaction_hash)} for r in rows]
