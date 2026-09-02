from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.verification import Verification
from app.services.article_service import fetch_article
from app.services.ai_service import analyze_claim
from app.services.hash_service import content_hash
from app.services.blockchain_service import record_verification

router=APIRouter(prefix="/api/verify",tags=["verification"])

class VerifyRequest(BaseModel):
    claim: str = Field("", max_length=10000)
    url: str | None = None

class ReviewRequest(BaseModel):
    decision: str
    reviewer_id: str = "demo-user"

@router.post("")
async def verify(req: VerifyRequest, db: AsyncSession=Depends(get_db)):
    claim=req.claim.strip()
    article_text=""
    if req.url:
        try:
            title, article_text=await fetch_article(req.url)
            if not claim: claim=title
        except Exception as e:
            if not claim:
                raise HTTPException(400,"Could not fetch the URL. Please provide a claim or article text.")
    if not claim:
        raise HTTPException(400,"A claim or URL is required.")

    analysis=await analyze_claim(claim,article_text)
    vid="FL-"+uuid4().hex[:8].upper()
    chash=content_hash(claim+"|"+article_text)
    chain=await record_verification(vid,chash)
    row=Verification(id=vid,claim=claim,source_url=req.url,status=analysis["status"],
        trust_score=analysis["trust_score"],ai_confidence=analysis["ai_confidence"],
        evidence_strength=analysis["evidence_strength"],source_reliability=analysis["source_reliability"],
        community_agreement=0,explanation=analysis["explanation"],evidence=analysis["evidence"],
        content_hash=chash,blockchain_network=chain["network"],transaction_hash=chain["transaction_hash"])
    db.add(row); await db.commit()
    return serialize(row)

@router.get("/{verification_id}")
async def get_verification(verification_id:str,db:AsyncSession=Depends(get_db)):
    row=await db.get(Verification,verification_id)
    if not row: raise HTTPException(404,"Verification not found")
    return serialize(row)

@router.get("/{verification_id}/evidence")
async def get_evidence(verification_id:str,db:AsyncSession=Depends(get_db)):
    row=await db.get(Verification,verification_id)
    if not row: raise HTTPException(404,"Verification not found")
    return {"verification_id":row.id,"evidence":row.evidence}

@router.post("/{verification_id}/review")
async def review(verification_id:str,req:ReviewRequest,db:AsyncSession=Depends(get_db)):
    row=await db.get(Verification,verification_id)
    if not row: raise HTTPException(404,"Verification not found")
    # MVP: simple aggregate demo. Production should use a separate reviews table.
    if req.decision.upper() not in {"AGREE","DISAGREE","NEED_EVIDENCE"}:
        raise HTTPException(400,"Invalid decision")
    if req.decision.upper()=="AGREE":
        row.community_agreement=min(100,row.community_agreement+5)
    else:
        row.community_agreement=max(0,row.community_agreement-3)
    await db.commit()
    return {"verification_id":row.id,"community_agreement":row.community_agreement}

def serialize(row:Verification):
    return {
        "id":row.id,"claim":row.claim,"source_url":row.source_url,"status":row.status,
        "trust_score":row.trust_score,"ai_confidence":row.ai_confidence,
        "evidence_strength":row.evidence_strength,"source_reliability":row.source_reliability,
        "community_agreement":row.community_agreement,"explanation":row.explanation,
        "evidence":row.evidence,"content_hash":row.content_hash,
        "blockchain_network":row.blockchain_network,"transaction_hash":row.transaction_hash,
        "created_at":row.created_at.isoformat()
    }
