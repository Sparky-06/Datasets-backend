from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def get_root():
    return {"Python": "on Vercel"}


@app.post("/anything")
def post_anything():
    return {"Python": "on Vercel"}
