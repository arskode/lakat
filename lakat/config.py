from typing import List

import yaml
from pydantic import BaseModel


class Building(BaseModel):
    name: str
    level: int


class Castle(BaseModel):
    upgrades: List[Building]


class Fortress(BaseModel):
    upgrades: List[Building]


class City(BaseModel):
    upgrades: List[Building]


class AccountConfig(BaseModel):
    email: str
    password: str
    world: str

    missions: bool
    silver_barter_threshold: int

    castle: Castle
    fortress: Fortress
    city: City


class Config(BaseModel):
    profiles_path: str = "profiles"
    headless: bool = True
    interval: int

    debug: bool = False
    screenshots_path: str = "screenshots"

    accounts: List[AccountConfig]


def load_config() -> Config:
    with open("config.yml", mode="r", encoding="utf8") as config_file:
        yml = yaml.load(config_file, yaml.SafeLoader)

    return Config(**yml)
