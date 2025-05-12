"""Authentication service."""
import httpx
from core import config
from fastapi import HTTPException
from logger import logger  # Import the custom SQLite logger

class AuthenticationService:
    """Authentication service."""
    def __init__(self):
        self.base_url = f"{config.AUTHERIZATION_SERVER_URL}:{config.AUTHORIZATION_SERVER_PORT}"
        print(f"Base URL: {self.base_url}")
        self.headers = {"accept": "*/*", "Content-Type": "application/json"}
        self.timeout = 5  

    async def _authenticate(self, endpoint: str, jwt_token: str):
        url = f"{self.base_url}{endpoint}"
        payload = {"token": jwt_token}
        logger.info(f"Authenticating via {url}")
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(url, headers=self.headers, json=payload)
                response.raise_for_status()
                logger.info(f"Authentication succeeded for {url}")
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.warning(f"Authentication failed for {url} | Status: {e.response.status_code}")
                raise HTTPException(status_code=e.response.status_code, detail="Authentication failed")
            except Exception as e:
                logger.error(f"Unexpected error during authentication at {url}: {str(e)}")
                raise HTTPException(status_code=500, detail="Internal server error")

    async def authenticate_customer(self, jwt_token: str):
        logger.info("Authenticating customer...")
        return await self._authenticate(config.AUTHORIZATION_SERVER_CUSTOMER_ENDPOINT, jwt_token)

    async def authenticate_vendor(self, jwt_token: str):
        logger.info("Authenticating vendor...")
        return await self._authenticate(config.AUTHORIZATION_SERVER_VENDOR_ENDPOINT, jwt_token)

    async def authenticate_admin(self, jwt_token: str):
        logger.info("Authenticating admin...")
        return await self._authenticate(config.AUTHORIZATION_SERVER_ADMIN_ENDPOINT, jwt_token)

def get_auth_service():
    return AuthenticationService()
