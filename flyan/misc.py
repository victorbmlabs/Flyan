import json
from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional

currencies: dict = json.load(open("currencies.json"))
stations: dict = json.load(open("stations.json"))

class Flight(BaseModel):
    pass

class FlightSearchParams(BaseModel):
    """Parameters for flight searches"""

    from_airport: str
    from_date: datetime
    date_to: datetime
    destination_country: Optional[str]
    max_price: Optional[int]
    to_airport: Optional[str]
    departure_time_from: Optional[str] = "00:00"
    departure_time_to: Optional[str] = "23:59"

    @field_validator("from_airport")
    def validate_airport(cls, v):
        if isinstance(v, str) and v in stations.keys():
            return v.upper()

        raise ValueError("Airport code must be a 3-letter IATA code")

    @field_validator("date_from", "date_to")
    def validate_dates(cls, v):
        if v < datetime.now():
            raise ValueError("Date from or to cannot be in the past")

        return v

    @field_validator("max_price")
    def validate_price(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Price can't be negative")
        
        return v
    
    def to_api_params(self) -> dict:
        """Convert the parameters to the format expected by the Ryanair API"""
        params = {
            "departureAirportIataCode": self.departure_airport,
            "outboundDepartureDateFrom": self.date_from.date().isoformat(),
            "outboundDepartureDateTo": self.date_to.date().isoformat(),
            "outboundDepartureTimeFrom": self.departure_time_from,
            "outboundDepartureTimeTo": self.departure_time_to,
        }
        
        if self.destination_country:
            params["arrivalCountryCode"] = self.destination_country

        if self.max_price:
            params["priceValueTo"] = self.max_price

        if self.destination_airport:
            params["arrivalAirportIataCode"] = self.destination_airport
            
        if self.custom_params:
            params.update(self.custom_params)
            
        return params

class ReturnFlightSearchParams(FlightSearchParams):
    """Parameters for return flight searches"""
    return_date_from: datetime
    return_date_to: datetime
    inbound_departure_time_from: Optional[str] = "00:00"
    inbound_departure_time_to: Optional[str] = "23:59"

    @field_validator('return_date_from', 'return_date_to')
    def validate_return_dates(cls, v, values):
        if 'date_from' in values and v < values['date_from']:
            raise ValueError('Return date cannot be before departure date')
        return v

    def to_api_params(self) -> dict:
        """Convert the parameters to the format expected by the Ryanair API"""
        params = super().to_api_params()
        params.update({
            "inboundDepartureDateFrom": self.return_date_from.date().isoformat(),
            "inboundDepartureDateTo": self.return_date_to.date().isoformat(),
            "inboundDepartureTimeFrom": self.inbound_departure_time_from,
            "inboundDepartureTimeTo": self.inbound_departure_time_to,
        })
        return params