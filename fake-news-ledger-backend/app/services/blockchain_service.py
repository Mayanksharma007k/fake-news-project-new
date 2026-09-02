import hashlib
from app.config import settings

async def record_verification(verification_id: str, content_hash: str):
    # Hackathon-safe abstraction. Add web3 contract transaction here when configured.
    if settings.blockchain_rpc_url and settings.contract_address and settings.private_key:
        # Intentionally left as an integration point: keep private keys server-side.
        # Return a real transaction hash after wiring your deployed contract.
        pass
    demo_tx="0x"+hashlib.sha256((verification_id+content_hash).encode()).hexdigest()
    return {"network":"Demo/Testnet","transaction_hash":demo_tx}
