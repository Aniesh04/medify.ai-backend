from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from os import environ as env 

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    env_var = "fail"
    try:
        env_var = env["TEST_ENV_VARIABLE"]
    except:
        pass
    return {"message": "Medify.ai 🎉", "ENV_ACCESS": env_var}