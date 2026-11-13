"""
Helper classes for handling the JWT auth in the app

For now very basic authorization, only checks whether the
jwt is a valid one.
"""

import httpx
import jwt
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient
from pydantic import BaseModel


class User(BaseModel):
    username: str
    vos: list[str] | None = None


class JWTAuthenticator(HTTPBearer):
    def __init__(self, *, issuer: str | None = None, httpx_client=None, **kwargs):
        super().__init__(**kwargs)
        self.issuer = issuer
        self._jwks_client = None
        if httpx_client:
            self.httpx_client = httpx_client
        else:
            self.httpx_client = httpx.AsyncClient()

    async def _get_jwks_client(self):
        if self._jwks_client:
            return self._jwks_client
        r = await self.httpx_client.get(
            f"{self.issuer}/.well-known/openid-configuration",
        )
        r.raise_for_status()
        jwks_uri = r.json()["jwks_uri"]
        self._jwks_client = PyJWKClient(jwks_uri)
        return self._jwks_client

    async def get_user(self, credentials: HTTPAuthorizationCredentials) -> User | None:
        if not credentials:
            if self.auto_error:
                raise self.make_not_authenticated_error()
            else:
                return None
        jwks_client = await self._get_jwks_client()
        token = credentials.credentials
        try:
            signing_key = jwks_client.get_signing_key_from_jwt(token)
            payload = jwt.decode(
                token,
                signing_key,
                algorithms=["RS256"],
            )
            return User(username=payload["sub"], vos=[])
        except jwt.exceptions.DecodeError:
            if self.auto_error:
                raise self.make_not_authenticated_error()
            else:
                return None
