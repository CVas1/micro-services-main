"""Api dependencies."""
from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from services.auth_service import AuthenticationService, get_auth_service

api_key_header = APIKeyHeader(name="Authorization", auto_error=True)

async def admin_auth_dependency(
    token: str = Security(api_key_header),
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    try:
        # first, only admins are allowed
        await auth_service.authenticate_admin(token)
    except HTTPException as http_exc:
        # propagate any 401/403 from authenticate_admin
        raise http_exc
    except Exception:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {"status": "authenticated"}


async def vendor_auth_dependency(
    token: str = Security(api_key_header),
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    try:
        # first, let admins through
        try:
            await auth_service.authenticate_admin(token)
            return {"status": "authenticated"}
        except HTTPException:
            # not an admin → try vendor
            await auth_service.authenticate_vendor(token)
    except HTTPException as http_exc:
        raise http_exc
    except Exception:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {"status": "authenticated"}


async def customer_auth_dependency(
    token: str = Security(api_key_header),
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    try:
        await auth_service.authenticate_customer(token)
    except HTTPException as http_exc:
        raise http_exc
    except Exception:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {"status": "authenticated"}


async def any_user_auth_dependency(
    token: str = Security(api_key_header),
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    try:
        # admins first
        try:
            await auth_service.authenticate_admin(token)
            return {"status": "authenticated"}
        except HTTPException:
            # then customer
            try:
                await auth_service.authenticate_customer(token)
                return {"status": "authenticated"}
            except HTTPException:
                # lastly vendor
                await auth_service.authenticate_vendor(token)
    except HTTPException as http_exc:
        raise http_exc
    except Exception:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {"status": "authenticated"}
