import requests


class API:
    def __init__(self, api_key):
        self._api_key = api_key

    def get_airport_details(self, code_iata_airport: str) -> dict:
        url = f"https://aviation-edge.com/v2/public/airportDatabase?codeIataAirport={code_iata_airport}&key={self._api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            res = response.json()
            if "success" not in res:
                return {"data": res[0], "success": True}
            else:
                return {"data": [], "success": False}
        else:
            return {}

    def fetch_flight_data(self, depIata: str, limit: int = 10) -> list:
        url = f"https://aviation-edge.com/v2/public/flights?key={self._api_key}&depIata={depIata}&status=en-route&limit={limit}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return []
