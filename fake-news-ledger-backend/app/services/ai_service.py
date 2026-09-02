import json
from app.config import settings

async def analyze_claim(claim: str, article_text: str = "") -> dict:
    # Uses an LLM when OPENAI_API_KEY is configured; otherwise returns safe demo data.
    if not settings.openai_api_key:
        return demo_analysis(claim)

    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        prompt = f'''
Analyze the following news claim. Do not declare absolute truth. Return JSON only.
Classify as SUPPORTED, UNCERTAIN, MISLEADING, or HIGH_RISK.
Give a confidence estimate, reasoning, and evidence signals. Do not invent sources.

CLAIM:
{claim}

ARTICLE:
{article_text[:12000]}
'''
        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role":"system","content":"You are an evidence-oriented misinformation analysis assistant."},
                {"role":"user","content":prompt}
            ],
            temperature=0.1,
            response_format={"type":"json_object"}
        )
        data=json.loads(response.choices[0].message.content)
        return normalize(data, claim)
    except Exception:
        return demo_analysis(claim)

def normalize(data: dict, claim: str) -> dict:
    return {
        "status": str(data.get("status","UNCERTAIN")).upper(),
        "trust_score": max(0,min(100,int(data.get("trust_score",50)))),
        "ai_confidence": max(0,min(100,int(data.get("ai_confidence",60)))),
        "evidence_strength": max(0,min(100,int(data.get("evidence_strength",40)))),
        "source_reliability": max(0,min(100,int(data.get("source_reliability",40)))),
        "explanation": data.get("explanation","The available information is insufficient for a strong conclusion."),
        "evidence": data.get("evidence",[])
    }

def demo_analysis(claim: str) -> dict:
    return {
        "status":"HIGH_RISK",
        "trust_score":23,
        "ai_confidence":81,
        "evidence_strength":18,
        "source_reliability":25,
        "explanation":"Demo assessment: the claim should be treated cautiously because no verified primary evidence has been supplied. This is not a guarantee that the claim is false.",
        "evidence":[
            {"type":"CONTRADICTS","source":"Official source placeholder","reliability":98,"text":"No matching primary announcement was supplied for this demo."},
            {"type":"SUPPORTS","source":"Unverified source placeholder","reliability":31,"text":"The claim is repeated without a verifiable primary source."}
        ]
    }
