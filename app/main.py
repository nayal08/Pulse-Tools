from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.models import *
import uuid
import json
import sys
from app.core.config import settings
from app.routers import users,projects
from app import models, schemas
from app.database import SessionLocal, engine

def get_application():
    _app = FastAPI(title=settings.PROJECT_NAME)

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return _app


app = get_application()

models.Base.metadata.create_all(bind=engine)

app.include_router(users.router,prefix="/api")
app.include_router(projects.router,prefix="/projects")

data =[]
