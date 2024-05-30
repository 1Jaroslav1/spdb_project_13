from pydantic import BaseModel
from typing import Optional


class Aircraft(BaseModel):
    iataCode: str
    icao24: str
    icaoCode: str
    regKey: str


class Airline(BaseModel):
    iataCode: str
    icaoCode: str


class Airport(BaseModel):
    iata2Code: str
    icao2Code: str


class FlightInfo(BaseModel):
    iataNumber: str
    icaoNumber: str
    number: str


class Geography(BaseModel):
    altitude: float
    direction: int
    latitude: float
    longitude: float


class Speed(BaseModel):
    horizontal: float
    isGround: int
    vspeed: int


class System(BaseModel):
    squawk: Optional[str]
    updated: int


class FlightModel(BaseModel):
    aircraft: Aircraft
    airline: Airline
    arrival: Airport
    departure: Airport
    flight: FlightInfo
    geography: Geography
    speed: Speed
    status: str
    system: System

class AirportModel(BaseModel):
    GMT: str
    airportId: int
    codeIataAirport: str
    codeIataCity: str
    codeIcaoAirport: str
    codeIso2Country: str
    geonameId: str
    latitudeAirport
