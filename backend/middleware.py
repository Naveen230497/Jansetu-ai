from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import time
from .logger import logger

# In-memory dictionary for basic rate limiting (Enterprise uses Redis)
REQUESTS_TRACKER = {}
RATE_LIMIT = 100 # requests per minute

async def enterprise_security_middleware(request: Request, call_next):
    client_ip = request.client.host
    current_time = time.time()
    
    # 1. Rate Limiting Logic
    if client_ip not in REQUESTS_TRACKER:
        REQUESTS_TRACKER[client_ip] = []
        
    # Clean up old requests (older than 60 seconds)
    REQUESTS_TRACKER[client_ip] = [t for t in REQUESTS_TRACKER[client_ip] if current_time - t < 60]
    
    if len(REQUESTS_TRACKER[client_ip]) >= RATE_LIMIT:
        logger.warning(f"Security Alert: Rate limit exceeded by IP {client_ip}")
        return JSONResponse(
            status_code=429, 
            content={"error": "Enterprise Security: Too many requests. Rate limit exceeded."}
        )
        
    REQUESTS_TRACKER[client_ip].append(current_time)
    
    # 2. Add Security Headers
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    return response
