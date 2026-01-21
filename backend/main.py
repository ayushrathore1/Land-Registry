"""
Land Record Digitization Tool - FastAPI Backend
Main application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from routes import search, parcels, reconciliation, auth
from services.data_service import DataService

# Initialize data service
data_service = DataService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load data on startup"""
    data_service.load_all_data()
    yield


app = FastAPI(
    title="Land Record Digitization API",
    description="API for correlating textual land records with spatial parcel boundaries",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(search.router, prefix="/api/search", tags=["Search"])
app.include_router(parcels.router, prefix="/api/parcels", tags=["Parcels"])
app.include_router(reconciliation.router, prefix="/api/reconciliation", tags=["Reconciliation"])


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Land Record Digitization API",
        "version": "1.0.0"
    }


@app.get("/api/stats")
async def get_stats():
    """Get overall statistics"""
    return data_service.get_statistics()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
