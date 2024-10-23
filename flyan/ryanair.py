import logging

import httpx
from misc import currencies, FlightSearchParams, ReturnFlightSearchParams
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)


logger = logging.getLogger("Flyan")
if not logger.handlers:
    logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s.%(msecs)03d %(levelname)s:%(message)s", datefmt="%Y-%m-%d %I:%M:%S"
    )

    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


class RyanairException(Exception):
    def __init__(self, message):
        super().__init__(f"Ryanair API: {message}")


class RyanAir:
    """
    Create a RyanAir instance

    :param str currency: Preferred currency
    """

    BASE_SERVICES_API_URL = "https://services-api.ryanair.com/farfnd/v4/"
    AGGREGATE_URL = "https://www.ryanair.com/api/views/locate/3/aggregate/all/en"

    def __init__(self, currency: str = "EUR"):
        self.client = httpx.Client()
        self.__get("https://ryanair.com")

        if currency in currencies.keys():
            self.currency = currency

        else:
            self.currency = "EUR"

    def __del__(self):
        self.client.close()

    @retry(
        stop=stop_after_attempt(5),  # Retry up to 5 times
        wait=wait_exponential(),
        retry=retry_if_exception_type(Exception),
        reraise=True,  # Raise the exception after retries are exhausted
    )
    def __get(self, url: str, params: dict = {}) -> httpx.Response:
        """
        Send a GET request to url

        :param str url: The url to GET
        :param dict params: URL Parameters for the query
        :return httpx.Response: Response object
        :raises httpx.HTTPStatusError: If one occurred
        """
        response = self.client.get(url, params=params)
        response.raise_for_status()
        return response

    def get_oneways(self, params: FlightSearchParams):
        """
        Get oneways
        """
