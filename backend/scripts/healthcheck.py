#!/usr/bin/env python3
"""
Health check script for the FastAPI application.
Returns exit code 0 if healthy, 1 if unhealthy.
"""
import sys
import httpx
import os


def check_health() -> bool:
    """Perform health check against the application."""
    host = os.getenv("HEALTH_CHECK_HOST", "localhost")
    port = os.getenv("HEALTH_CHECK_PORT", "8000")
    url = f"http://{host}:{port}/health/"
    
    try:
        response = httpx.get(url, timeout=5.0)
        
        if response.status_code != 200:
            print(f"Health check failed: HTTP {response.status_code}", file=sys.stderr)
            return False
        
        data = response.json()
        
        # Check overall status
        if data.get("status") != "healthy":
            print(f"Application status: {data.get('status')}", file=sys.stderr)
            return False
        
        # Check database status
        if data.get("database") != "healthy":
            print(f"Database status: {data.get('database')}", file=sys.stderr)
            return False
        
        print("Health check passed")
        return True
        
    except httpx.TimeoutException:
        print("Health check failed: Request timeout", file=sys.stderr)
        return False
    except httpx.ConnectError:
        print("Health check failed: Connection refused", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Health check failed: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    is_healthy = check_health()
    sys.exit(0 if is_healthy else 1)