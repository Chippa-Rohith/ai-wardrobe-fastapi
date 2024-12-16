from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import attributePredict, wardrobe

# Initialize FastAPI app
app = FastAPI(title="Fashion Attribute Prediction API")

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend's origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Include routers for different endpoints
app.include_router(attributePredict.router, prefix="/api/v1/attributePredict", tags=["Attribute Prediction"])
app.include_router(wardrobe.router, prefix="/api/v1/wardrobe", tags=["Wardrobe"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Fashion Attribute Prediction API!"}