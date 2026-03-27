from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class SeverityLevel(Enum):
    BAJO = "bajo"
    MEDIO = "medio"
    ALTO = "alto"
    CRITICO = "critico"


class IncidentCategory(Enum):
    SEGURIDAD = "seguridad"
    INFRAESTRUCTURA = "infraestructura"
    SERVICIOS = "servicios"
    AMBIENTAL = "ambiental"
    TRANSITO = "transito"
    OTRO = "otro"


@dataclass
class Location:
    latitude: float
    longitude: float
    address: str
    city: str
    country: str
    postal_code: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "address": self.address,
            "city": self.city,
            "country": self.country,
            "postal_code": self.postal_code,
        }

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> Optional["Location"]:
        if not data:
            return None
        return cls(
            latitude=data.get("latitude", 0.0),
            longitude=data.get("longitude", 0.0),
            address=data.get("address", ""),
            city=data.get("city", ""),
            country=data.get("country", ""),
            postal_code=data.get("postal_code"),
        )


@dataclass
class Incident:
    id: str = ""
    title: str = ""
    description: str = ""
    category: str = "otro"
    severity: str = "bajo"
    location: Dict[str, Any] = field(default_factory=dict)
    reporter_name: str = ""
    reporter_contact: str = ""
    created_at: str = ""
    status: str = "pendiente"
    updated_at: Optional[str] = None
    comments: Optional[List[str]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "Incident":
        if not data:
            data = {}
        data["location"] = data.get("location", {})
        data["comments"] = data.get("comments", [])
        return cls(**data)


@dataclass
class ReportFilters:
    category: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
