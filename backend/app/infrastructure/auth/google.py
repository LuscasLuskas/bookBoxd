import os
from typing import Dict
import httpx

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")


async def verify_google_token(id_token: str) -> Dict[str, str]:
    url = "https://oauth2.googleapis.com/tokeninfo"
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url, params={"id_token": id_token})
        response.raise_for_status()
        data = response.json()

    if GOOGLE_CLIENT_ID and data.get("aud") != GOOGLE_CLIENT_ID:
        raise ValueError("Google token audience mismatch")

    if data.get("email_verified") not in ("true", True, 1, "1"):
        raise ValueError("Google account email not verified")

    return {
        "email": data["email"],
        "sub": data["sub"],
        "name": data.get("name"),
    }
