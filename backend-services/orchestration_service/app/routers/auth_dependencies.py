"""Authentication dependencies for routers."""
from fastapi import HTTPException, Request, Depends
from services.auth_http_client import get_auth_service, AuthenticationService
from logger import logger

async def authenticate_user(request: Request, auth_service: AuthenticationService = Depends(get_auth_service)):
    """Dependency to authenticate any type of user (customer, vendor, or admin)."""
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    try:
        # Try authenticating as each user type
        try:
            await auth_service.authenticate_customer(auth_header)
            return "customer"
        except HTTPException:
            try:
                await auth_service.authenticate_vendor(auth_header)
                return "vendor"
            except HTTPException:
                try:
                    await auth_service.authenticate_admin(auth_header)
                    return "admin"
                except HTTPException:
                    raise HTTPException(status_code=401, detail="Invalid authentication token")
    except Exception as e:
        logger.log(f"Authentication failed: {str(e)}", level="ERROR")
        raise HTTPException(status_code=401, detail="Authentication failed")

async def authenticate_admin(request: Request, auth_service: AuthenticationService = Depends(get_auth_service)):
    """Dependency to ensure only admin users can access the endpoint."""
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    try:
        await auth_service.authenticate_admin(auth_header)
    except Exception as e:
        logger.log(f"Admin authentication failed: {str(e)}", level="ERROR")
        raise HTTPException(status_code=401, detail="Admin authentication failed") 