import json
import time
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator

currencies: dict = json.load(open("./currencies.json", encoding="utf-8"))
stations: dict = json.load(open("./stations.json", encoding="utf-8"))


class Airport(BaseModel):
    country_name: str
    iata_code: str
    name: str
    seo_name: str
    city_name: str
    city_code: str
    city_country_code: str

class Flight(BaseModel):
    departure_airport: Airport
    arrival_airport: Airport
    departure_date: datetime
    arrival_date: datetime
    price: float
    currency: str
    flight_key: str
    flight_number: str
    previous_price: Optional[str | float]


class ReturnFlight(BaseModel):
    outbound: Flight
    inbound: Flight
    summary_price: float
    summary_currency: str
    previous_price: str | float


class FlightSearchParams(BaseModel):
    """Parameters for flight searches"""

    from_airport: str
    from_date: datetime
    to_date: datetime
    destination_country: Optional[str] = None
    max_price: Optional[int] = None
    to_airport: Optional[str] = None
    departure_time_from: Optional[str] = "00:00"
    departure_time_to: Optional[str] = "23:59"

    @field_validator("from_airport")
    def validate_airport(cls, v):
        if isinstance(v, str) and v in stations.keys():
            return v.upper()

        raise ValueError("Airport code must be a 3-letter IATA code")

    @field_validator("from_date", "to_date")
    def validate_dates(cls, v):
        if v < datetime.now():
            raise ValueError("Date from or to cannot be in the past")

        return v

    @field_validator("max_price")
    def validate_price(cls, v):
        if v is None:
            return v

        if v <= 0:
            raise ValueError("Price can't be negative")

        return v

    def to_api_params(self) -> dict:
        """Convert the parameters to the format expected by the Ryanair API"""
        params = {
            "departureAirportIataCode": self.from_airport,
            "outboundDepartureDateFrom": self.from_date.date().isoformat(),
            "outboundDepartureDateTo": self.to_date.date().isoformat(),
            "outboundDepartureTimeFrom": self.departure_time_from,
            "outboundDepartureTimeTo": self.departure_time_to,
        }

        if self.destination_country:
            params["arrivalCountryCode"] = self.destination_country

        if self.max_price:
            params["priceValueTo"] = self.max_price

        if self.to_airport:
            params["arrivalAirportIataCode"] = self.to_airport

        return params


class ReturnFlightSearchParams(FlightSearchParams):
    """Parameters for return flight searches"""

    return_date_from: datetime
    return_date_to: datetime
    inbound_departure_time_from: Optional[str] = "00:00"
    inbound_departure_time_to: Optional[str] = "23:59"

    @field_validator("return_date_from", "return_date_to")
    def validate_return_dates(cls, v, values):
        if "date_from" in values and v < values["date_from"]:
            raise ValueError("Return date cannot be before departure date")
        return v

    def to_api_params(self) -> dict:
        """Convert the parameters to the format expected by the Ryanair API"""
        params = super().to_api_params()
        params.update(
            {
                "inboundDepartureDateFrom": self.return_date_from.date().isoformat(),
                "inboundDepartureDateTo": self.return_date_to.date().isoformat(),
                "inboundDepartureTimeFrom": self.inbound_departure_time_from,
                "inboundDepartureTimeTo": self.inbound_departure_time_to,
            }
        )
        return params
