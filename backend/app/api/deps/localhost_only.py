from typing import Annotated
from fastapi import Depends, HTTPException, Request, status


async def localhost_only(request: Request) -> bool:
    """Dependency to restrict access to localhost only."""
    client_host = request.client.host if request.client else None
    
    # Allow localhost/loopback addresses
    allowed_hosts = {"127.0.0.1", "::1", "localhost"}
    
    if client_host not in allowed_hosts:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. This endpoint is only available from localhost."
        )
    
    return True

LocalhostDep = Annotated[bool, Depends(localhost_only)]