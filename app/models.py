from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, List
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


@dataclass
class Incident:
    id: str
    title: str
    description: str
    category: str
    severity: str
    location: dict
    reporter_name: str
    reporter_contact: str
    created_at: str
    status: str = "pendiente"
    updated_at: Optional[str] = None
    comments: Optional[List[str]] = None

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        data["location"] = data.get("location", {})
        return cls(**data)


@dataclass
class ReportFilters:
    category: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
