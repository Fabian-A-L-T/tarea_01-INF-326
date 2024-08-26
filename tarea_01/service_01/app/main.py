import logging

from time import sleep
from pymongo import MongoClient
from bson.objectid import ObjectId
from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI()
mongodb_client = MongoClient("service_01_mongodb", 27017)

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')


class Driver(BaseModel):
    id: str | None = None
    name: str
    country: str
    team: str
    team_id: str | None = None
    podiums: int = ""

    def __init__(self, **kargs):
        if "_id" in kargs:
            kargs["id"] = str(kargs["_id"])
        BaseModel.__init__(self, **kargs)


@app.get("/")
async def root():
    logging.info("👋 Hello world (end-point)!")
    return {"Hello": "World"}


@app.get("/drivers",
         response_model=list[Driver])
def drivers_all(team_id: str | None = None):
    """Prueba"""
    logging.info(f"Getting all drivers (team_id: {team_id})")
    filters = {}

    sleep(3)

    if team_id:
        filters["team_id"] = team_id

    return [Driver(**driver) for driver in mongodb_client.service_01.drivers.find(filters)]


@app.get("/driver/{driver_id}")
def drivers_get(driver_id: str):
    return Driver(**mongodb_client.service_01.drivers.find_one({"_id": ObjectId(driver_id)}))


@app.delete("/driver/{driver_id}")
def drivers_delete(driver_id: str):
    mongodb_client.service_01.drivers.delete_one(
        {"_id": ObjectId(driver_id)}
    )
    return "ok"


@app.post("/drivers")
def drivers_create(driver: Driver):
    inserted_id = mongodb_client.service_01.drivers.insert_one(
        driver.dict()
    ).inserted_id

    new_driver = Driver(
        **mongodb_client.service_01.drivers.find_one(
            {"_id": ObjectId(inserted_id)}
        )
    )

    logging.info(f"✨ New driver created: {new_driver}")

    return new_driver
