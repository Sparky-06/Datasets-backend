from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"Python": "on Vercel"}

@app.post("/anything")
def post_anything():
    return {"Python": "on Vercel"}
