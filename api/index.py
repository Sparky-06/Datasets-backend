from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "ok"}

@app.post("/anything")
async def anything():
    return {"status": "posted"}
