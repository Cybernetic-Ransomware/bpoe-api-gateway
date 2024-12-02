from fastapi import FastAPI, Depends

from src.auth.router import router as auth_router
app = FastAPI()
app.include_router(auth_router, prefix="/log", tags=["auth"])

@app.get("/")
async def root():
    return {"message": "Hello World"}
