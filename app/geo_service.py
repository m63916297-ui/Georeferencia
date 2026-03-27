import requests
from typing import Optional, Dict, Any, List
from .models import Location
import os


class GeoapifyService:
    BASE_URL = "https://api.geoapify.com/v1"

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get(
            "GEOAPIFY_API_KEY", "b4be52d95c1543b99864371eb4562a37"
        )

    def geocode(self, address: str) -> Optional[Location]:
        url = f"{self.BASE_URL}/geocode/search"
        params = {"text": address, "apiKey": self.api_key, "format": "json"}

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("results") and len(data["results"]) > 0:
                result = data["results"][0]
                return Location(
                    latitude=result.get("lat", 0),
                    longitude=result.get("lon", 0),
                    address=result.get("address_line1", ""),
                    city=result.get("city", result.get("county", "")),
                    country=result.get("country", ""),
                    postal_code=result.get("postcode"),
                )
        except requests.RequestException as e:
            print(f"Error en geocodificación: {e}")
        return None

    def reverse_geocode(self, latitude: float, longitude: float) -> Optional[Location]:
        url = f"{self.BASE_URL}/geocode/reverse"
        params = {
            "lat": latitude,
            "lon": longitude,
            "apiKey": self.api_key,
            "format": "json",
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("results") and len(data["results"]) > 0:
                result = data["results"][0]
                return Location(
                    latitude=latitude,
                    longitude=longitude,
                    address=result.get("address_line1", ""),
                    city=result.get("city", result.get("county", "")),
                    country=result.get("country", ""),
                    postal_code=result.get("postcode"),
                )
        except requests.RequestException as e:
            print(f"Error en geocodificación inversa: {e}")
        return None

    def search_places(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        url = f"{self.BASE_URL}/geocode/search"
        params = {
            "text": query,
            "apiKey": self.api_key,
            "format": "json",
            "limit": limit,
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])
        except requests.RequestException as e:
            print(f"Error en búsqueda de lugares: {e}")
            return []

    def get_ip_location(self) -> Optional[Location]:
        url = f"{self.BASE_URL}/geocode/ip"
        params = {"apiKey": self.api_key}

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("location"):
                loc = data["location"]
                return Location(
                    latitude=loc.get("lat", 0),
                    longitude=loc.get("lon", 0),
                    address="",
                    city=loc.get("city", ""),
                    country=loc.get("country", ""),
                )
        except requests.RequestException as e:
            print(f"Error obteniendo ubicación por IP: {e}")
        return None
