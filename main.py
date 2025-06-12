from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from routers import adminRoutes, itemRoutes, userRoutes, authRoutes  # Import your routers

from logger import setup_logger  # Assuming you have a logger setup in logger.py
from logging import INFO, DEBUG, ERROR, WARNING, CRITICAL

import datetime

from auth import get_current_active_user

# Configuration
APP_VERSION = "0.0.4"

logger = setup_logger("FastAPI_Boilerplate", file_log_level=DEBUG, console_log_level=WARNING)
logger.debug("Starting FastAPI application... Version: %s", APP_VERSION)

# Initialize FastAPI app
app = FastAPI(
    title="My FastAPI Boilerplate Service",
    description="A FastAPI backend service with authentication",
    version=APP_VERSION
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging Middleware
@app.middleware("http")
async def log_requests(request, call_next):
    response = await call_next(request)
    # Here you can log the request and response details
    logger.info(f"Request: {request.method} {request.url} - Response: {response.status_code}")
    return response

# Custom exception handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found", "error": "NOT_FOUND"}
    )

@app.exception_handler(500)
async def internal_server_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": "INTERNAL_ERROR"}
    )

# Public routes
@app.get("/")
async def root():
    return {"message": "Welcome to the API", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.datetime.now(datetime.UTC)}

app.include_router(adminRoutes.router, prefix="/admin", tags=["admin"], dependencies=[Depends(get_current_active_user)])
app.include_router(authRoutes.router, prefix="/auth", tags=["auth"])
app.include_router(itemRoutes.router, prefix="/items", tags=["items"], dependencies=[Depends(get_current_active_user)])
app.include_router(userRoutes.router, prefix="/users", tags=["users"], dependencies=[Depends(get_current_active_user)])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)