from datetime import datetime, timezone
from sqlalchemy import String, Text, Integer, Float, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class Verification(Base):
    __tablename__ = "verifications"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    claim: Mapped[str] = mapped_column(Text)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30))
    trust_score: Mapped[int] = mapped_column(Integer)
    ai_confidence: Mapped[int] = mapped_column(Integer)
    evidence_strength: Mapped[int] = mapped_column(Integer)
    source_reliability: Mapped[int] = mapped_column(Integer)
    community_agreement: Mapped[int] = mapped_column(Integer, default=0)
    explanation: Mapped[str] = mapped_column(Text)
    evidence: Mapped[list] = mapped_column(JSON, default=list)
    content_hash: Mapped[str] = mapped_column(String(64))
    blockchain_network: Mapped[str] = mapped_column(String(50), default="Demo/Testnet")
    transaction_hash: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
