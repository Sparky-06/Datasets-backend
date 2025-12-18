from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Python": "on Vercel"}


@app.post("/anythin")
def read_root():
    return {"Python": "on Vercel"}
