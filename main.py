from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ciyexa_backend.api.v1.endpoints import agent, crypto # Import new crypto endpoints
from ciyexa_backend.core.config import settings
from ciyexa_backend.utils.logger import setup_logging

# Setup logging
setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(agent.router, prefix="/api/v1", tags=["Agent"])
app.include_router(crypto.router, prefix="/api/v1", tags=["Crypto Data"]) # Include new crypto router

@app.get("/")
async def root():
    return {"message": "Welcome to Ciyexa AI LLM Crypto Agent Backend!"}
