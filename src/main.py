from fastapi import FastAPI, Depends

from src.auth.config import auth

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/priv", dependencies=[Depends(auth.implicit_scheme)])
async def get_private():
    return {"message": "Hello World but in prvate"}
