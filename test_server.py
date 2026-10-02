

from fastapi import FastAPI
from ivr_handler import ivr_router


app = FastAPI(
    title="KrishiSetu AI - IVR",
    description="AI-powered Agriculture IVR System",
    version="1.0.0"
)


# Include IVR routes
app.include_router(ivr_router)


@app.get("/")
async def home():

    return {
        "message": "KrishiSetu AI IVR Server is Running",
        "status": "active"
    }