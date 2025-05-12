"""Api dependencies."""
from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from services.auth_service import AuthenticationService, get_auth_service
from logger import logger


api_key_header = APIKeyHeader(name="Authorization", auto_error=True)

async def admin_auth_dependency(
    token: str = Security(api_key_header),
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    try:
        await auth_service.authenticate_admin(token)
    except HTTPException as http_exc:
        raise http_exc
    except Exception as exc:
        logger.error(f"Admin authentication failed: {str(exc)}")
        raise HTTPException(status_code=401, detail="Authentication failed")
    return {"status": "authenticated"}

async def customer_auth_dependency(
    token: str = Security(api_key_header),
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    try:
        await auth_service.authenticate_customer(token)
    except HTTPException as http_exc:
        raise http_exc
    except Exception as exc:
        logger.error(f"Customer authentication failed: {str(exc)}")
        raise HTTPException(status_code=401, detail="Authentication failed")
    return {"status": "authenticated"}

async def vendor_auth_dependency(
    token: str = Security(api_key_header),
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    try:
        await auth_service.authenticate_vendor(token)
    except HTTPException as http_exc:
        raise http_exc
    except Exception as exc:
        logger.error(f"Vendor authentication failed: {str(exc)}")
        raise HTTPException(status_code=401, detail="Authentication failed")
    return {"status": "authenticated"}
