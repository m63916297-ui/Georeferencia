import requests
from requests.structures import CaseInsensitiveDict
from typing import Optional, Dict, Any, List
from .models import Location
import os


GEOAPIFY_API_KEY = "b4be52d95c1543b99864371eb4562a37"
GEOAPIFY_BASE_URL = "https://api.geoapify.com/v1"


class GeoapifyService:
    GEOCODE_URL = f"{GEOAPIFY_BASE_URL}/geocode/search"
    REVERSE_GEOCODE_URL = f"{GEOAPIFY_BASE_URL}/geocode/reverse"
    IP_GEOCODE_URL = f"{GEOAPIFY_BASE_URL}/geocode/ip"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key: str = api_key or os.environ.get(
            "GEOAPIFY_API_KEY", GEOAPIFY_API_KEY
        )

    def _make_request(
        self, url: str, params: Dict[str, Any] = None
    ) -> Optional[Dict[str, Any]]:
        headers = CaseInsensitiveDict()
        headers["Accept"] = "application/json"

        try:
            resp = requests.get(url, headers=headers, params=params, timeout=15)
            if resp.status_code == 200:
                return resp.json()
        except requests.RequestException as e:
            print(f"Request error: {e}")
        return None

    def geocode(self, address: str) -> Optional[Location]:
        if not address or not address.strip():
            return None

        params = {"text": address.strip(), "apiKey": self.api_key}

        data = self._make_request(self.GEOCODE_URL, params)

        if data and data.get("results") and len(data["results"]) > 0:
            result = data["results"][0]
            return Location(
                latitude=result.get("lat", 0.0),
                longitude=result.get("lon", 0.0),
                address=result.get("address_line1", "") or "",
                city=result.get("city", "") or result.get("county", "") or "",
                country=result.get("country", "") or "",
                postal_code=result.get("postcode"),
            )
        return None

    def reverse_geocode(self, latitude: float, longitude: float) -> Optional[Location]:
        params = {"lat": latitude, "lon": longitude, "apiKey": self.api_key}

        data = self._make_request(self.REVERSE_GEOCODE_URL, params)

        if data and data.get("results") and len(data["results"]) > 0:
            result = data["results"][0]
            return Location(
                latitude=latitude,
                longitude=longitude,
                address=result.get("address_line1", "") or "",
                city=result.get("city", "") or result.get("county", "") or "",
                country=result.get("country", "") or "",
                postal_code=result.get("postcode"),
            )
        else:
            return Location(
                latitude=latitude,
                longitude=longitude,
                address=f"({latitude}, {longitude})",
                city="Unknown",
                country="Unknown",
            )

    def search_places(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        if not query or not query.strip():
            return []

        params = {
            "text": query.strip(),
            "apiKey": self.api_key,
            "limit": min(limit, 20),
        }

        data = self._make_request(self.GEOCODE_URL, params)

        if data:
            return data.get("results", [])
        return []

    def get_ip_location(self) -> Optional[Location]:
        params = {"apiKey": self.api_key}

        data = self._make_request(self.IP_GEOCODE_URL, params)

        if data and data.get("location"):
            loc = data["location"]
            return Location(
                latitude=loc.get("lat", 0.0),
                longitude=loc.get("lon", 0.0),
                address="",
                city=loc.get("city", "") or "Unknown",
                country=loc.get("country", "") or "Unknown",
            )
        return None

    def get_autocomplete(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        if not query or len(query) < 3:
            return []

        params = {
            "text": query.strip(),
            "apiKey": self.api_key,
            "limit": min(limit, 10),
        }

        data = self._make_request(self.GEOCODE_URL, params)

        if data:
            return data.get("results", [])
        return []

    def test_connection(self) -> bool:
        try:
            location = self.geocode("Bogota, Colombia")
            return location is not None
        except Exception:
            return False


geo_service = GeoapifyService()
