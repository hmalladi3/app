from fastapi import FastAPI
from pydantic import BaseModel
from uuid import UUID, uuid4

app = FastAPI()

@app.get("/")
def read():
    return {"my":"nga"}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
