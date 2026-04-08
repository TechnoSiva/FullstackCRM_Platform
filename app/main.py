from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers.activity_router import router as activity_router
from app.routers.auth_router import router as auth_router
from app.routers.dashboard_router import router as dashboard_router
from app.routers.lead_router import router as lead_router
from app.routers.opportunity_router import router as opportunity_router
from app.routers.user_router import router as user_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Enterprise CRM & Sales Intelligence")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(lead_router)
app.include_router(opportunity_router)
app.include_router(activity_router)
app.include_router(dashboard_router)


@app.get("/health")
def health():
    return {"status": "ok"}
