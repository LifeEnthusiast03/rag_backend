from fastapi import FastAPI,Header,Depends
from fastapi.middleware.cors import CORSMiddleware
from db.database import engine
from db import data_models
from route.chat_route.chat_router import router as chat_router
from route.upload_route.upload_router import router as upload_router
from route.auth_route.auth_router import router as auth_router
from models.pymodel import userdataforapi
from typing import Annotated
from utils.routeprotect import get_current_user
app = FastAPI()


# Creating tables in postgrsql
# data_models.Base.metadata.create_all(bind=engine)
# print("tables created")
# Enable CORS for your React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Vite's default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Added Auth route
app.include_router(auth_router)

# Added upload Router
app.include_router(upload_router)
#Adder chat router
app.include_router(chat_router)
# Home route
@app.get("/")
def read_root():
    return {"message": "PDF Upload API is running"}
# Health route
@app.get("/health")
def cheak_health():
    return {"health":"okay"}

@app.get("/protected")
def protected_route(user:Annotated[userdataforapi,Depends(get_current_user)]):
    return {
        "user": user
    }
