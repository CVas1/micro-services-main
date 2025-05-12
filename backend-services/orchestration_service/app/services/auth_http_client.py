"""Authentication service."""
import httpx
from fastapi import HTTPException
import config
from logger import logger

class AuthenticationService:
    """Authentication service."""
    def __init__(self):
        self.base_url = f"{config.AUTHERIZATION_SERVER_HOST}:{config.AUTHORIZATION_SERVER_PORT}"
        print(f"Base URL: {self.base_url}")
        self.headers = {"accept": "*/*", "Content-Type": "application/json"}
        self.timeout = 5  

    async def _authenticate(self, endpoint: str, jwt_token: str):
        url = f"{self.base_url}{endpoint}"
        payload = {"token": jwt_token}
        logger.log(f"Attempting authentication at endpoint: {endpoint}")
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(url, headers=self.headers, json=payload)
                response.raise_for_status()
                logger.log(f"Authentication successful for endpoint: {endpoint}")
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.log(f"Authentication failed with status {e.response.status_code} for endpoint: {endpoint}", level="ERROR")
                raise HTTPException(status_code=e.response.status_code, detail="Authentication failed")
            except Exception as e:
                logger.log(f"Unexpected error during authentication for endpoint {endpoint}: {str(e)}", level="ERROR")
                raise HTTPException(status_code=500, detail="Internal server error")

    async def authenticate_customer(self, jwt_token: str):
        return await self._authenticate(config.AUTHORIZATION_SERVER_CUSTOMER_ENDPOINT, jwt_token)

    async def authenticate_vendor(self, jwt_token: str):
        return await self._authenticate(config.AUTHORIZATION_SERVER_VENDOR_ENDPOINT, jwt_token)

    async def authenticate_admin(self, jwt_token: str):
        return await self._authenticate(config.AUTHORIZATION_SERVER_ADMIN_ENDPOINT, jwt_token)

def get_auth_service() -> AuthenticationService:
    return AuthenticationService()
