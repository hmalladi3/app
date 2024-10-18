from fastapi import FastAPI
from pydantic import BaseModel
from uuid import UUID, uuid4

from db import db
from account import Account, Service, Review

from math import radians, sin, cos, sqrt, atan2

app = FastAPI()

# cols: usr:str, pwd:str, complete:bool, verified:bool, loc:(lat, long)
db.create_table("Accounts")
# cols: usr:str, name:str, desc:str, price:float
db.create_table("Services")
# cols: usr:str, stars:float, title:str, body:str
db.create_table("Reviews")

# helper function finding the distance between two points
def dist(loc1:tuple[float, float], loc2:tuple[float, float]):
    # haversine formula
    R = 3959  # Earth's radius in miles

    lat1, lon1 = radians(loc1[0]), radians(loc1[1])
    lat2, lon2 = radians(loc2[0]), radians(loc2[1])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))

    return R * c


@app.get("/")
def read():
    return {"my":"nga"}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
