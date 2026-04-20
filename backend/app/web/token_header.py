import os
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from config import prop

api_key_header = APIKeyHeader(name="X-Token", auto_error=False)


async def verify_token(token: str = Security(api_key_header)):
    expected = os.environ.get(prop['web']['token'])
    if not token or token != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다.",
            headers={"WWW-Authenticate": "X-Token"},
        )
    return token
