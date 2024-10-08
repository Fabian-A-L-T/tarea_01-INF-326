from enum import Enum

import logging
import requests
from pymongo import MongoClient
from bson.objectid import ObjectId

from fastapi import FastAPI, Query
from pydantic import BaseModel


app = FastAPI()
mongodb_client = MongoClient("service_02_mongodb", 27017)

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')


class Driver(BaseModel):
    id: str | None = None
    name: str
    country: str
    team: str
    team_id: str | None = None
    podiums: str = ""


class Country(str, Enum):
    belgica = 'Belgica'
    uk = 'Reino Unido'
    italia = 'Italia'

class Team(BaseModel):
    id: str | None = None
    name: str
    base: Country

    power_unit: str = ""
    base_chassis: str = ""

    def __init__(self, **kargs):
        if "_id" in kargs:
            kargs["id"] = str(kargs["_id"])
        BaseModel.__init__(self, **kargs)


@app.get("/")
async def root():
    return {"Hello": "World"}


def get_drivers_of_a_team(team_id) -> list[Driver]:
        url = f"http://service_01:80/drivers?team_id={team_id}"
        logging.info(f"🌍 Request [GET] {url}")

        return requests.get(url).json()

@app.get("/teams")
def teams_all(expand: list[str] = Query(default=[])):
    teams = [Team(**team).dict()
             for team in mongodb_client.service_02.teams.find({})]

    # n+1 problem...
    if expand and 'drivers' in expand:
        logging.warning("🚨 n+1 requests...")
        for i, team in enumerate(teams):
            teams[i]["drivers"] = get_drivers_of_a_team(team['id'])

    return teams


@app.get("/teams/{team_id}")
def teams_get(team_id: str, expand: list[str] = Query(default=[])):
    team = Team(
        **mongodb_client.service_02.teams.find_one({"_id": ObjectId(team_id)})
    ).dict()

    if expand and 'drivers' in expand:
        team["drivers"] = get_drivers_of_a_team(team_id)

    return team


@app.delete("/teams/{team_id}")
def teams_delete(team_id: str):
    mongodb_client.service_02.teams.delete_one({"_id": ObjectId(team_id)})
    return {"status": "ok"}


@app.post("/teams")
def teams_create(team: Team):
    inserted_id = mongodb_client.service_02.teams.insert_one(
        team.dict()
    ).inserted_id

    new_team = Team(
        **mongodb_client.service_02.teams.find_one(
            {"_id": ObjectId(inserted_id)}
        )
    )

    logging.info(f"✨ New team created: {new_team}")

    return new_team
