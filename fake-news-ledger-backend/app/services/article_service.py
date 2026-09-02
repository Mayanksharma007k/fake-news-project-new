import httpx
from bs4 import BeautifulSoup

async def fetch_article(url: str) -> tuple[str,str]:
    async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
        r=await client.get(url, headers={"User-Agent":"FakeNewsLedger/1.0"})
        r.raise_for_status()
    soup=BeautifulSoup(r.text,"html.parser")
    title=soup.title.get_text(" ",strip=True) if soup.title else ""
    for tag in soup(["script","style","noscript"]):
        tag.decompose()
    text=" ".join(soup.stripped_strings)
    return title, text[:20000]
