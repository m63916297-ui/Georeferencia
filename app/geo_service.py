import requests
from typing import Optional, Dict, Any, List
from .models import Location
import os


GEOAPIFY_DEFAULT_KEY = "b4be52d95c1543b99864371eb4562a37"


class GeoapifyService:
    BASE_URL = "https://api.geoapify.com/v1"
    GEOCODE_URL = "https://api.geoapify.com/v1/geocode/search"
    REVERSE_GEOCODE_URL = "https://api.geoapify.com/v1/geocode/reverse"
    IP_GEOCODE_URL = "https://api.geoapify.com/v1/geocode/ip"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key: str = api_key or os.environ.get(
            "GEOAPIFY_API_KEY", GEOAPIFY_DEFAULT_KEY
        )
        if not self.api_key:
            self.api_key = GEOAPIFY_DEFAULT_KEY

    def geocode(self, address: str) -> Optional[Location]:
        if not address or not address.strip():
            return None

        params = {
            "text": address.strip(),
            "apiKey": self.api_key,
            "format": "json",
            "limit": 1,
        }

        try:
            response = requests.get(self.GEOCODE_URL, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            if data.get("results") and len(data["results"]) > 0:
                result = data["results"][0]
                return Location(
                    latitude=result.get("lat", 0.0),
                    longitude=result.get("lon", 0.0),
                    address=result.get("address_line1", "") or "",
                    city=result.get("city", "") or result.get("county", "") or "",
                    country=result.get("country", "") or "",
                    postal_code=result.get("postcode"),
                )
        except requests.RequestException as e:
            print(f"Error en geocodificación: {e}")
        except Exception as e:
            print(f"Error inesperado en geocodificación: {e}")
        return None

    def reverse_geocode(self, latitude: float, longitude: float) -> Optional[Location]:
        params = {
            "lat": latitude,
            "lon": longitude,
            "apiKey": self.api_key,
            "format": "json",
        }

        try:
            response = requests.get(self.REVERSE_GEOCODE_URL, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            if data.get("results") and len(data["results"]) > 0:
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
                    city="Desconocida",
                    country="Desconocido",
                )
        except requests.RequestException as e:
            print(f"Error en geocodificación inversa: {e}")
            return Location(
                latitude=latitude,
                longitude=longitude,
                address=f"({latitude}, {longitude})",
                city="Desconocida",
                country="Desconocido",
            )
        except Exception as e:
            print(f"Error inesperado en geocodificación inversa: {e}")
            return None

    def search_places(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        if not query or not query.strip():
            return []

        params = {
            "text": query.strip(),
            "apiKey": self.api_key,
            "format": "json",
            "limit": min(limit, 20),
        }

        try:
            response = requests.get(self.GEOCODE_URL, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])
        except requests.RequestException as e:
            print(f"Error en búsqueda de lugares: {e}")
            return []
        except Exception as e:
            print(f"Error inesperado en búsqueda de lugares: {e}")
            return []

    def get_ip_location(self) -> Optional[Location]:
        params = {"apiKey": self.api_key}

        try:
            response = requests.get(self.IP_GEOCODE_URL, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            if data.get("location"):
                loc = data["location"]
                return Location(
                    latitude=loc.get("lat", 0.0),
                    longitude=loc.get("lon", 0.0),
                    address="",
                    city=loc.get("city", "") or "Desconocida",
                    country=loc.get("country", "") or "Desconocido",
                )
        except requests.RequestException as e:
            print(f"Error obteniendo ubicación por IP: {e}")
        except Exception as e:
            print(f"Error inesperado: {e}")
        return None

    def get_autocomplete(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        if not query or len(query) < 3:
            return []

        params = {
            "text": query.strip(),
            "apiKey": self.api_key,
            "format": "json",
            "limit": min(limit, 10),
        }

        try:
            response = requests.get(self.GEOCODE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])
        except requests.RequestException as e:
            print(f"Error en autocompletado: {e}")
            return []

    def test_connection(self) -> bool:
        try:
            location = self.geocode("Bogotá, Colombia")
            return location is not None
        except Exception:
            return False
