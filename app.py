"""
🛡️ SAFE GeoReport - Sistema de Gestión de Incidentes
=====================================================

Sistema de Reporte de Incidentes Georreferenciados
Basado en: Segmentación Estratégica de Variables de Reporte
API: Geoapify (b4be52d95c1543b99864371eb4562a37)

Autor: SAFE Inteligencia Segura
Versión: 2.0.0
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
import folium
from folium.plugins import Fullscreen, LocateControl
from streamlit_folium import st_folium
import requests
from requests.structures import CaseInsensitiveDict
import os
import json
import uuid


# =============================================================================
# CONFIGURACIÓN PRINCIPAL
# =============================================================================

# API de Geoapify (del archivo Geo APIKEY.txt)
GEOAPIFY_API_KEY = "b4be52d95c1543b99864371eb4562a37"
GEOAPIFY_BASE_URL = "https://api.geoapify.com/v1"
GEOCODE_URL = f"{GEOAPIFY_BASE_URL}/geocode/search"
REVERSE_GEOCODE_URL = f"{GEOAPIFY_BASE_URL}/geocode/reverse"
IP_GEOCODE_URL = f"{GEOAPIFY_BASE_URL}/geocode/ip"
MAP_TILES_URL = f"https://maps.geoapify.com/v1/tile/carto/{{z}}/{{x}}/{{y}}.png?apiKey={GEOAPIFY_API_KEY}"

DEFAULT_MAP_CENTER = [6.2442, -75.5812]
DEFAULT_ZOOM = 12
DATA_FILE = "georeferencia/data/incidents.json"


# =============================================================================
# ZONAS DE MEDELLÍN Y ÁREA METROPOLITANA
# =============================================================================

ZONAS_MEDELLIN = {
    "medellin_centro": {
        "nombre": "Centro de Medellín",
        "lat": 6.2447,
        "lon": -75.5745,
        "comunas": ["La Candelaria", "Los Nietos", "Barrio Pablo Escobar"],
    },
    "el_poblado": {
        "nombre": "El Poblado",
        "lat": 6.2081,
        "lon": -75.5686,
        "comunas": ["El Poblado", "Manrique", "La Mansion"],
    },
    "laureles": {
        "nombre": "Laureles - Estadio",
        "lat": 6.2565,
        "lon": -75.5918,
        "comunas": ["Laureles", "Estadio", "Bolivia"],
    },
    "belen": {
        "nombre": "Belén - Fatima",
        "lat": 6.2278,
        "lon": -75.6044,
        "comunas": ["Belén", "Fatima", "Granada"],
    },
    "envigado": {
        "nombre": "Envigado",
        "lat": 6.1758,
        "lon": -75.5586,
        "comunas": ["Envigado", "El Rosario", "La Magnolia"],
    },
    "itagui": {
        "nombre": "Itagüí",
        "lat": 6.1847,
        "lon": -75.6006,
        "comunas": ["Itagüí", "La Mayorca", "El Rosario"],
    },
    "sabaneta": {
        "nombre": "Sabaneta",
        "lat": 6.1502,
        "lon": -75.6168,
        "comunas": ["Sabaneta", "Aures", "La Doctora"],
    },
    "bello": {
        "nombre": "Bello",
        "lat": 6.3373,
        "lon": -75.5576,
        "comunas": ["Bello", "Niquía", "Cabañas"],
    },
    "copacabana": {
        "nombre": "Copacabana",
        "lat": 6.3463,
        "lon": -75.5426,
        "comunas": ["Copacabana", "San Jose", "La Gabriela"],
    },
    "girardota": {
        "nombre": "Girardota",
        "lat": 6.3772,
        "lon": -75.4945,
        "comunas": ["Girardota", "Centro", "El Raizal"],
    },
    "barbosa": {
        "nombre": "Barbosa",
        "lat": 6.4367,
        "lon": -75.5269,
        "comunas": ["Barbosa", "Centro", "San Jose"],
    },
    "la_estrella": {
        "nombre": "La Estrella",
        "lat": 6.1298,
        "lon": -75.6316,
        "comunas": ["La Estrella", "El Pedrero", "San Joaquin"],
    },
    "caldas": {
        "nombre": "Caldas",
        "lat": 6.0925,
        "lon": -75.6357,
        "comunas": ["Caldas", "La Paz", "El Progreso"],
    },
    "santa_elena": {
        "nombre": "Santa Elena",
        "lat": 6.2730,
        "lon": -75.5030,
        "comunas": ["Santa Elena", "Palmitas", "San Cristobal"],
    },
    "la_candelaria": {
        "nombre": "La Candelaria - Prado",
        "lat": 6.2550,
        "lon": -75.5620,
        "comunas": ["La Candelaria", "Prado", "Junín"],
    },
    "manrique": {
        "nombre": "Manrique",
        "lat": 6.2820,
        "lon": -75.5380,
        "comunas": ["Manrique", "Las Granjas", "Campo Valdes"],
    },
    "robledo": {
        "nombre": "Robledo",
        "lat": 6.2690,
        "lon": -75.5950,
        "comunas": ["Robledo", "El Volador", "Barrio Cerro"],
    },
    "guayabal": {
        "nombre": "Guayabal",
        "lat": 6.2270,
        "lon": -75.5570,
        "comunas": ["Guayabal", "San Guillermo", "Cristo Rey"],
    },
    "la_america": {
        "nombre": "La América",
        "lat": 6.2650,
        "lon": -75.6070,
        "comunas": ["La América", "Floresta", "Santa Monica"],
    },
    "san_javier": {
        "nombre": "San Javier",
        "lat": 6.2480,
        "lon": -75.6360,
        "comunas": ["San Javier", "La Palmeta", "El Salado"],
    },
}


# =============================================================================
# SEGMENTACIÓN ESTRATÉGICA DE VARIABLES DE REPORTE
# =============================================================================


class SegmentacionReporte:
    """
    Segmentación Estratégica de Variables de Reporte
    Basado en: SEGMENTACIÓN ESTRATÉGICA DE LAS VARIABLES DE REPORTE
    - Panel de Acceso Directo (6 categorías)
    - Incidentes de Convivencia (Ley 1801/2016)
    - Delitos de Bajo/Mediano Impacto (Ley 599/2000)
    """

    # ==================== PANEL DE ACCESO DIRECTO (Variables de Mayor Interés Territorial) ====================
    class Categoria:
        HURTO_PERSONAS = {
            "id": "hurto_personas",
            "nombre": "Hurto a Personas",
            "icono": "🎯",
            "descripcion": "Reportes rápidos de robos sin violencia extrema",
            "ley": None,
            "subcategorias": [],
        }

        HURTO_COMERCIOS = {
            "id": "hurto_comercios",
            "nombre": "Hurto a Comercios",
            "icono": "🏪",
            "descripcion": "Incidentes de robo en establecimientos locales",
            "ley": None,
            "subcategorias": [],
        }

        HURTO_VEHICULOS = {
            "id": "hurto_vehiculos",
            "nombre": "Hurto a Vehículos",
            "icono": "🚗",
            "descripcion": "Incluye partes de vehículos y motocicletas",
            "ley": None,
            "subcategorias": [],
        }

        HURTO_RESIDENCIAS = {
            "id": "hurto_residencias",
            "nombre": "Hurto a Residencias",
            "icono": "🏠",
            "descripcion": "Violación de la propiedad privada",
            "ley": None,
            "subcategorias": [],
        }

        VIOLENCIA_INTRAFAMILIAR = {
            "id": "violencia_intrafamiliar",
            "nombre": "Violencia Intrafamiliar",
            "icono": "⚠️",
            "descripcion": "Reportes de agresiones dentro del núcleo hogar",
            "ley": None,
            "subcategorias": [],
        }

        EXTORSION = {
            "id": "extorsion",
            "nombre": "Extorsión",
            "icono": "💰",
            "descripcion": "Cobros indebidos o vacunas en sectores comerciales",
            "ley": None,
            "subcategorias": [],
        }

        @classmethod
        def todas(cls):
            return [
                cls.HURTO_PERSONAS,
                cls.HURTO_COMERCIOS,
                cls.HURTO_VEHICULOS,
                cls.HURTO_RESIDENCIAS,
                cls.VIOLENCIA_INTRAFAMILIAR,
                cls.EXTORSION,
            ]

    # ==================== INCIDENTES DE CONVIVENCIA (Ley 1801/2016) ====================
    class Convivencia:
        ALTERACIONES_ORDEN = {
            "id": "alteraciones_orden",
            "nombre": "Alteraciones al Orden Público",
            "icono": "📢",
            "descripcion": "Reportes de comportamiento disruptivo en espacios públicos",
            "ley": "Ley 1801/2016",
        }

        EXTORSION_MENOR = {
            "id": "extorsion_menor",
            "nombre": "Extorsión Menor",
            "icono": "💵",
            "descripcion": "Cobros indebidos o vacunas en sectores comerciales",
            "ley": "Ley 1801/2016",
        }

        HURTO_COMERCIOS = {
            "id": "hurto_comercios_conv",
            "nombre": "Hurto a Comercios",
            "icono": "🏪",
            "descripcion": "Incidentes de robo en establecimientos locales",
            "ley": "Ley 1801/2016",
        }

        HURTO_PERSONAS = {
            "id": "hurto_personas_conv",
            "nombre": "Hurto a Personas",
            "icono": "🎯",
            "descripcion": "Reportes rápidos de robos sin violencia extrema",
            "ley": "Ley 1801/2016",
        }

        HURTO_RESIDENCIAS = {
            "id": "hurto_residencias_conv",
            "nombre": "Hurto a Residencias",
            "icono": "🏠",
            "descripcion": "Violación de la propiedad privada",
            "ley": "Ley 1801/2016",
        }

        HURTO_VEHICULOS = {
            "id": "hurto_vehiculos_conv",
            "nombre": "Hurto a Vehículos",
            "icono": "🚗",
            "descripcion": "Incluye partes de vehículos y motocicletas",
            "ley": "Ley 1801/2016",
        }

        LESIONES_PERSONALES = {
            "id": "lesiones_personales",
            "nombre": "Lesiones Personales",
            "icono": "🩹",
            "descripcion": "Conflictos físicos menores",
            "ley": "Ley 1801/2016",
        }

        RINAS_CALLEJERAS = {
            "id": "rinas_callejeras",
            "nombre": "Riñas Callejeras",
            "icono": "👊",
            "descripcion": "Peleas en vía pública",
            "ley": "Ley 1801/2016",
        }

        RUIDO_EXCESIVO = {
            "id": "ruido_excesivo",
            "nombre": "Ruido Excesivo",
            "icono": "🔊",
            "descripcion": "Contaminación auditiva que afecta la paz vecinal",
            "ley": "Ley 1801/2016",
        }

        VANDALISMO = {
            "id": "vandalismo",
            "nombre": "Vandalismo",
            "icono": "🔨",
            "descripcion": "Daños a bienes públicos o privados",
            "ley": "Ley 1801/2016",
        }

        VIOLENCIA_INTRAFAMILIAR = {
            "id": "violencia_intrafamiliar_conv",
            "nombre": "Violencia Intrafamiliar",
            "icono": "⚠️",
            "descripcion": "Reportes de agresiones dentro del núcleo hogar",
            "ley": "Ley 1801/2016",
        }

        OTRO_CONVIVENCIA = {
            "id": "otro_convivencia",
            "nombre": "Otro (¿Cuál?)",
            "icono": "📝",
            "descripcion": "Campo de texto abierto para casos no tipificados",
            "ley": "Ley 1801/2016",
        }

        @classmethod
        def todos(cls):
            return [
                cls.ALTERACIONES_ORDEN,
                cls.EXTORSION_MENOR,
                cls.HURTO_COMERCIOS,
                cls.HURTO_PERSONAS,
                cls.HURTO_RESIDENCIAS,
                cls.HURTO_VEHICULOS,
                cls.LESIONES_PERSONALES,
                cls.RINAS_CALLEJERAS,
                cls.RUIDO_EXCESIVO,
                cls.VANDALISMO,
                cls.VIOLENCIA_INTRAFAMILIAR,
                cls.OTRO_CONVIVENCIA,
            ]

    # ==================== DELITOS DE BAJO Y MEDIANO IMPACTO (Ley 599/2000) ====================
    class Delitos:
        DELITOS_SEXUALES = {
            "id": "delitos_sexuales",
            "nombre": "Delitos Sexuales Menores",
            "icono": "🚫",
            "descripcion": "Casos que requieren manejo de evidencia confidencial",
            "ley": "Ley 599/2000",
        }

        EXTORSION = {
            "id": "extorsion_delito",
            "nombre": "Extorsión",
            "icono": "💰",
            "descripcion": "Denuncia formal para investigación institucional",
            "ley": "Ley 599/2000",
        }

        HURTO_PERSONAS = {
            "id": "hurto_personas_delito",
            "nombre": "Hurto a Personas",
            "icono": "🎯",
            "descripcion": "Modalidades de atraco o raponazo bajo tipificación legal",
            "ley": "Ley 599/2000",
        }

        HURTO_RESIDENCIAS = {
            "id": "hurto_residencias_delito",
            "nombre": "Hurto a Residencias",
            "icono": "🏠",
            "descripcion": "Ingreso ilegal con fines de lucro",
            "ley": "Ley 599/2000",
        }

        HURTO_VEHICULOS = {
            "id": "hurto_vehiculos_delito",
            "nombre": "Hurto a Vehículos/Motocicletas",
            "icono": "🏍️",
            "descripcion": "Robo de vehículos motorizados para rastreo judicial",
            "ley": "Ley 599/2000",
        }

        LESIONES_PERSONALES = {
            "id": "lesiones_personales_delito",
            "nombre": "Lesiones Personales",
            "icono": "🩹",
            "descripcion": "Agresiones físicas documentadas para procesos legales",
            "ley": "Ley 599/2000",
        }

        VIOLENCIA_GENERO = {
            "id": "violencia_genero",
            "nombre": "Violencia de Género",
            "icono": "⚧️",
            "descripcion": "Denuncias específicas protegidas por protocolos de seguridad",
            "ley": "Ley 599/2000",
        }

        VIOLENCIA_INTRAFAMILIAR = {
            "id": "violencia_intrafamiliar_delito",
            "nombre": "Violencia Intrafamiliar",
            "icono": "⚠️",
            "descripcion": "Escalamiento de conflictos domésticos a instancias judiciales",
            "ley": "Ley 599/2000",
        }

        OTRO_DELITO = {
            "id": "otro_delito",
            "nombre": "Otro (¿Cuál?)",
            "icono": "📝",
            "descripcion": "Selección para delitos que no figuren en el menú principal",
            "ley": "Ley 599/2000",
        }

        @classmethod
        def todos(cls):
            return [
                cls.DELITOS_SEXUALES,
                cls.EXTORSION,
                cls.HURTO_PERSONAS,
                cls.HURTO_RESIDENCIAS,
                cls.HURTO_VEHICULOS,
                cls.LESIONES_PERSONALES,
                cls.VIOLENCIA_GENERO,
                cls.VIOLENCIA_INTRAFAMILIAR,
                cls.OTRO_DELITO,
            ]

    # ==================== TIPO DE REPORTE ====================
    class TipoReporte:
        RAPIDO = {
            "id": "rapido",
            "nombre": "Panel de Acceso Directo",
            "descripcion": "6 categorías de mayor interés territorial",
            "ley": None,
        }
        CONVIVENCIA = {
            "id": "convivencia",
            "nombre": "Incidentes de Convivencia",
            "descripcion": "Ley 1801/2016 - Código de Policía",
            "ley": "Ley 1801/2016",
        }
        DELITO = {
            "id": "delito",
            "nombre": "Delitos de Bajo/Mediano Impacto",
            "descripcion": "Ley 599/2000 - Código Penal",
            "ley": "Ley 599/2000",
        }

        @classmethod
        def todos(cls):
            return [cls.RAPIDO, cls.CONVIVENCIA, cls.DELITO]

    # ==================== NIVELES DE SEVERIDAD ====================
    class Severidad:
        CRITICO = {
            "id": "critico",
            "nombre": "Crítico",
            "icono": "⛔",
            "color": "darkred",
            "descripcion": "Riesgo inmediato a vidas o propiedad",
            "nivel": 4,
        }

        ALTO = {
            "id": "alto",
            "nombre": "Alto",
            "icono": "🔴",
            "color": "red",
            "descripcion": "Impacto significativo requiere atención urgente",
            "nivel": 3,
        }

        MEDIO = {
            "id": "medio",
            "nombre": "Medio",
            "icono": "🟠",
            "color": "orange",
            "descripcion": "Impacto moderado requiere atención",
            "nivel": 2,
        }

        BAJO = {
            "id": "bajo",
            "nombre": "Bajo",
            "icono": "🟢",
            "color": "green",
            "descripcion": "Impacto minimo o cosmetico",
            "nivel": 1,
        }

        @classmethod
        def todas(cls):
            return [cls.CRITICO, cls.ALTO, cls.MEDIO, cls.BAJO]

    # ==================== ESTADOS DEL REPORTE ====================
    class Estado:
        RECIBIDO = {"id": "recibido", "nombre": "Recibido", "icono": "📥"}
        VALIDANDO = {"id": "validando", "nombre": "Validando", "icono": "🔍"}
        ASIGNADO = {"id": "asignado", "nombre": "Asignado", "icono": "👤"}
        EN_PROCESO = {"id": "en_proceso", "nombre": "En Proceso", "icono": "⚙️"}
        RESUELTO = {"id": "resuelto", "nombre": "Resuelto", "icono": "✅"}
        CERRADO = {"id": "cerrado", "nombre": "Cerrado", "icono": "🔒"}
        RECHAZADO = {"id": "rechazado", "nombre": "Rechazado", "icono": "X"}

        @classmethod
        def todos(cls):
            return [
                cls.RECIBIDO,
                cls.VALIDANDO,
                cls.ASIGNADO,
                cls.EN_PROCESO,
                cls.RESUELTO,
                cls.CERRADO,
                cls.RECHAZADO,
            ]

    # ==================== PRIORIDADES ====================
    class Prioridad:
        URGENTE = {"id": "urgente", "nombre": "Urgente", "dias": 1}
        ALTA = {"id": "alta", "nombre": "Alta", "dias": 3}
        MEDIA = {"id": "media", "nombre": "Media", "dias": 7}
        BAJA = {"id": "baja", "nombre": "Baja", "dias": 15}

        @classmethod
        def todas(cls):
            return [cls.URGENTE, cls.ALTA, cls.MEDIA, cls.BAJA]

    # ==================== FUENTES DE REPORTE ====================
    class Fuente:
        CIUDADANO = {"id": "ciudadano", "nombre": "Ciudadano", "icono": "👤"}
        CAMARAS = {"id": "camaras", "nombre": "Cámaras de Seguridad", "icono": "📹"}
        SENSORES = {"id": "sensores", "nombre": "Sensores IoT", "icono": "📡"}
        EMERGENCIAS = {
            "id": "emergencias",
            "nombre": "Línea de Emergencias",
            "icono": "📞",
        }
        WEB = {"id": "web", "nombre": "Portal Web", "icono": "🌐"}
        MOVIL = {"id": "movil", "nombre": "App Móvil", "icono": "📱"}
        SOCIAL = {"id": "social", "nombre": "Redes Sociales", "icono": "📢"}

        @classmethod
        def todas(cls):
            return [
                cls.CIUDADANO,
                cls.CAMARAS,
                cls.SENSORES,
                cls.EMERGENCIAS,
                cls.WEB,
                cls.MOVIL,
                cls.SOCIAL,
            ]

    # ==================== IMPACTO ====================
    class Impacto:
        MUY_ALTO = {"id": "muy_alto", "nombre": "Muy Alto", "afectados": ">1000"}
        ALTO = {"id": "alto", "nombre": "Alto", "afectados": "100-1000"}
        MEDIO = {"id": "medio", "nombre": "Medio", "afectados": "10-100"}
        BAJO = {"id": "bajo", "nombre": "Bajo", "afectados": "1-10"}

        @classmethod
        def todo(cls):
            return [cls.MUY_ALTO, cls.ALTO, cls.MEDIO, cls.BAJO]


# Mapeos para UI
def get_all_categories():
    all_cats = []
    for c in SegmentacionReporte.Categoria.todas():
        c_copy = c.copy()
        all_cats.append(c_copy)
    for c in SegmentacionReporte.Convivencia.todos():
        c_copy = c.copy()
        all_cats.append(c_copy)
    for c in SegmentacionReporte.Delitos.todos():
        c_copy = c.copy()
        all_cats.append(c_copy)
    return all_cats


def get_all_incident_types():
    types = []
    for c in SegmentacionReporte.Convivencia.todos():
        types.append(
            {"id": c["id"], "nombre": c["nombre"], "icono": c["icono"], "ley": c["ley"]}
        )
    for c in SegmentacionReporte.Delitos.todos():
        types.append(
            {"id": c["id"], "nombre": c["nombre"], "icono": c["icono"], "ley": c["ley"]}
        )
    return types


CATEGORY_EMOJI = {c["id"]: c["icono"] for c in get_all_categories()}
SEVERITY_COLORS = {s["id"]: s["color"] for s in SegmentacionReporte.Severidad.todas()}


# =============================================================================
# SERVICIO DE GEOCODIFICACIÓN
# =============================================================================


class GeoapifyService:
    """Servicio de geocodificación usando Geoapify API"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or GEOAPIFY_API_KEY

    def _make_request(self, url: str, params: Dict = None) -> Optional[Dict]:
        headers = CaseInsensitiveDict()
        headers["Accept"] = "application/json"

        try:
            resp = requests.get(url, headers=headers, params=params, timeout=15)
            if resp.status_code == 200:
                return resp.json()
        except requests.RequestException as e:
            st.error(f"Error de conexión: {e}")
        return None

    def geocode(self, address: str) -> Optional[Dict]:
        if not address or not address.strip():
            return None

        params = {"text": address.strip(), "apiKey": self.api_key}
        data = self._make_request(GEOCODE_URL, params)

        if data and data.get("results") and len(data["results"]) > 0:
            result = data["results"][0]
            return {
                "latitude": result.get("lat", 0.0),
                "longitude": result.get("lon", 0.0),
                "address": result.get("address_line1", "") or "",
                "city": result.get("city", "") or result.get("county", "") or "",
                "country": result.get("country", "") or "",
                "postal_code": result.get("postcode"),
            }
        return None

    def reverse_geocode(self, lat: float, lon: float) -> Optional[Dict]:
        params = {"lat": lat, "lon": lon, "apiKey": self.api_key}
        data = self._make_request(REVERSE_GEOCODE_URL, params)

        if data and data.get("results") and len(data["results"]) > 0:
            result = data["results"][0]
            return {
                "latitude": lat,
                "longitude": lon,
                "address": result.get("address_line1", "") or "",
                "city": result.get("city", "") or result.get("county", "") or "",
                "country": result.get("country", "") or "",
                "postal_code": result.get("postcode"),
            }
        return {
            "latitude": lat,
            "longitude": lon,
            "address": f"({lat}, {lon})",
            "city": "Unknown",
            "country": "Unknown",
        }

    def get_ip_location(self) -> Optional[Dict]:
        params = {"apiKey": self.api_key}
        data = self._make_request(IP_GEOCODE_URL, params)

        if data and data.get("location"):
            loc = data["location"]
            return {
                "latitude": loc.get("lat", 0.0),
                "longitude": loc.get("lon", 0.0),
                "address": "",
                "city": loc.get("city", "") or "Unknown",
                "country": loc.get("country", "") or "Unknown",
            }
        return None

    def test_connection(self) -> bool:
        try:
            return self.geocode("Bogota, Colombia") is not None
        except Exception:
            return False


geo_service = GeoapifyService()


# =============================================================================
# ALMACENAMIENTO
# =============================================================================


class IncidentStorage:
    """Sistema de almacenamiento de incidentes"""

    def __init__(self, file_path: str = DATA_FILE):
        self.file_path = file_path
        self._ensure_file()

    def _ensure_file(self):
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as f:
                json.dump([], f)

    def _read(self) -> List[Dict]:
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _write(self, data: List[Dict]):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def create(self, incident: Dict) -> Dict:
        incidents = self._read()
        incident["id"] = str(uuid.uuid4())
        incident["created_at"] = datetime.now().isoformat()
        incident["updated_at"] = datetime.now().isoformat()
        incidents.append(incident)
        self._write(incidents)
        return incident

    def get_all(self) -> List[Dict]:
        return self._read()

    def update(self, incident_id: str, updates: Dict) -> Optional[Dict]:
        incidents = self._read()
        for i, inc in enumerate(incidents):
            if inc.get("id") == incident_id:
                inc.update(updates)
                inc["updated_at"] = datetime.now().isoformat()
                incidents[i] = inc
                self._write(incidents)
                return inc
        return None

    def delete(self, incident_id: str) -> bool:
        incidents = self._read()
        initial = len(incidents)
        incidents = [i for i in incidents if i.get("id") != incident_id]
        if len(incidents) < initial:
            self._write(incidents)
            return True
        return False

    def get_stats(self) -> Dict:
        incidents = self.get_all()
        return {
            "total": len(incidents),
            "by_category": self._count_by(incidents, "category"),
            "by_severity": self._count_by(incidents, "severity"),
            "by_status": self._count_by(incidents, "status"),
            "by_priority": self._count_by(incidents, "priority"),
            "by_impact": self._count_by(incidents, "impact"),
        }

    def _count_by(self, incidents: List[Dict], field: str) -> Dict:
        counts = {}
        for inc in incidents:
            val = inc.get(field)
            if val:
                counts[val] = counts.get(val, 0) + 1
        return counts


storage = IncidentStorage()


# =============================================================================
# INTERFAZ DE USUARIO
# =============================================================================


def init_session():
    if "map_center" not in st.session_state:
        st.session_state.map_center = DEFAULT_MAP_CENTER.copy()
    if "pending_location" not in st.session_state:
        st.session_state.pending_location = None
    if "location_confirmed" not in st.session_state:
        st.session_state.location_confirmed = False
    if "tipo_reporte" not in st.session_state:
        st.session_state.tipo_reporte = "rapido"
    if "report_category" not in st.session_state:
        st.session_state.report_category = SegmentacionReporte.Categoria.todas()[0][
            "id"
        ]


def render_header():
    st.set_page_config(
        page_title="SAFE GeoReport - Sistema de Incidentes",
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown(
        """
    <style>
    .safe-header {
        background: linear-gradient(135deg, #0D47A1 0%, #1565C0 50%, #1976D2 100%);
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
    }
    .safe-header h1 {
        color: white;
        margin: 0;
    }
    .badge {
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: bold;
    }
    .badge-provider {
        background: linear-gradient(90deg, #4CAF50, #2E7D32);
        color: white;
    }
    .badge-safe {
        background: linear-gradient(90deg, #FF9800, #F57C00);
        color: white;
    }
    .stat-box {
        background: #f5f5f5;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
    }
    .category-card {
        padding: 15px;
        border-radius: 10px;
        margin: 5px 0;
        border-left: 5px solid;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(
            """
        <div class="safe-header">
            <h1>🛡️ SAFE GeoReport</h1>
            <p>Sistema de Gestión de Incidentes - Segmentación Estratégica de Variables</p>
            <p style="font-size: 11px; color: #90CAF9;">🔗 API: https://api.geoapify.com/v1/geocode | Key: b4be52d95c1543b99864371eb4562a37</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            '<span class="badge badge-provider">🏢 PROVIDER ACTIVO</span>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<span class="badge badge-safe">🛡️ SAFE INTELIGENCIA</span>',
            unsafe_allow_html=True,
        )


def render_sidebar():
    st.sidebar.title("🗺️ Navegación")

    menu = [
        "🏠 Dashboard",
        "📝 Nuevo Reporte",
        "🗺️ Mapa Global",
        "📋 Todos los Reportes",
        "📈 Analytics",
        "⚙️ Configuración",
    ]

    choice = st.sidebar.radio("Menú", menu)

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Estadísticas Rápidas")

    stats = storage.get_stats()
    st.sidebar.metric("Total Reportes", stats["total"])

    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    ### 🛡️ SAFE Inteligencia
    **Versión:** 2.0.0
    
    **API Geoapify:** ✅
    - Geocoding: Activo
    - Maps: Activo
    - IP Location: Activo
    """)

    return choice


def create_map(incidents: List[Dict], center: List = None, zoom: int = DEFAULT_ZOOM):
    if center is None:
        center = DEFAULT_MAP_CENTER.copy()

    m = folium.Map(
        location=center,
        zoom_start=zoom,
        tiles=MAP_TILES_URL,
        attr='&copy; <a href="https://www.geoapify.com/">Geoapify</a>',
    )

    Fullscreen(position="topright").add_to(m)
    LocateControl(auto_start=False).add_to(m)

    for inc in incidents:
        loc = inc.get("location", {})
        lat, lon = loc.get("latitude", 0), loc.get("longitude", 0)

        if lat == 0 and lon == 0:
            continue

        cat, sev = inc.get("category", "seguridad"), inc.get("severity", "bajo")
        popup = f"""
        <div style="font-family: Arial; min-width: 280px;">
            <h4 style="color: #1565C0; margin: 0 0 10px 0;">{inc.get("title", "Sin título")}</h4>
            <p><b>📁 Categoría:</b> {CATEGORY_EMOJI.get(cat, "📌")} {inc.get("subcategoria", cat)}</p>
            <p><b>⚠️ Severidad:</b> <span style="color:{SEVERITY_COLORS.get(sev, "blue")}; font-weight:bold;">{sev.upper()}</span></p>
            <p><b>📊 Estado:</b> {inc.get("status", "recibido")}</p>
            <p><b>🎯 Prioridad:</b> {inc.get("priority", "media")}</p>
            <hr>
            <p style="font-size: 12px;">{inc.get("description", "")[:120]}...</p>
            <p style="font-size: 10px; color: #666;">📍 {loc.get("address", "N/A")}</p>
        </div>
        """

        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup, max_width=320),
            tooltip=f"{CATEGORY_EMOJI.get(cat, '📌')} {inc.get('title', '')}",
            icon=folium.Icon(color=SEVERITY_COLORS.get(sev, "blue"), icon="info-sign"),
        ).add_to(m)

        folium.CircleMarker(
            location=[lat, lon],
            radius=10,
            color=SEVERITY_COLORS.get(sev, "blue"),
            fill=True,
            fillOpacity=0.3,
            weight=2,
        ).add_to(m)

    return m


def render_stats(stats: Dict):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total", stats.get("total", 0))
    with col2:
        pend = stats.get("by_status", {}).get("recibido", 0)
        st.metric("Recibidos", pend)
    with col3:
        proc = stats.get("by_status", {}).get("en_proceso", 0)
        st.metric("En Proceso", proc)
    with col4:
        res = stats.get("by_status", {}).get("resuelto", 0)
        st.metric("Resueltos", res)

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("📁 Por Categoría")
        cat_data = stats.get("by_category", {})
        if cat_data:
            df = pd.DataFrame(list(cat_data.items()), columns=["Categoría", "Cantidad"])
            st.bar_chart(df.set_index("Categoría"))

    with col2:
        st.subheader("⚠️ Por Severidad")
        sev_data = stats.get("by_severity", {})
        if sev_data:
            df = pd.DataFrame(list(sev_data.items()), columns=["Severidad", "Cantidad"])
            st.bar_chart(df.set_index("Severidad"))

    with col3:
        st.subheader("🎯 Por Prioridad")
        pri_data = stats.get("by_priority", {})
        if pri_data:
            df = pd.DataFrame(list(pri_data.items()), columns=["Prioridad", "Cantidad"])
            st.bar_chart(df.set_index("Prioridad"))


# =============================================================================
# PÁGINAS
# =============================================================================


def page_dashboard():
    st.title("📊 Dashboard SAFE")
    st.markdown("### Sistema de Gestión de Incidentes - Segmentación Estratégica")

    stats = storage.get_stats()
    render_stats(stats)

    st.markdown("---")
    st.subheader("🗺️ Mapa de Incidentes")

    incidents = storage.get_all()
    col_map, col_side = st.columns([3, 1])

    with col_map:
        if incidents:
            m = create_map(incidents, st.session_state.map_center)
            st_folium(m, width=800, height=500, key="dash_map")
        else:
            m = create_map([], DEFAULT_MAP_CENTER)
            st_folium(m, width=800, height=500)
            st.info("No hay incidentes registrados")

    with col_side:
        st.markdown("#### 📋 Panel de Acceso Directo")
        for cat in SegmentacionReporte.Categoria.todas():
            count = stats.get("by_category", {}).get(cat["id"], 0)
            st.markdown(f"{cat['icono']} **{cat['nombre']}**: {count}")

        st.markdown("#### ⚖️ Convivencia (Ley 1801)")
        for cat in SegmentacionReporte.Convivencia.todos():
            count = stats.get("by_category", {}).get(cat["id"], 0)
            if count > 0:
                st.markdown(f"{cat['icono']} **{cat['nombre']}**: {count}")

        st.markdown("#### ⚖️ Delitos (Ley 599)")
        for cat in SegmentacionReporte.Delitos.todos():
            count = stats.get("by_category", {}).get(cat["id"], 0)
            if count > 0:
                st.markdown(f"{cat['icono']} **{cat['nombre']}**: {count}")


def page_report():
    st.title("📝 Nuevo Reporte de Incidente")
    st.markdown("### Segmentación Estratégica de Variables de Reporte")
    st.markdown("*Basado en: SEGMENTACIÓN ESTRATÉGICA DE LAS VARIABLES DE REPORTE*")

    st.markdown("---")
    st.subheader(
        "🎯 1. Panel de Acceso Directo (Variables de Mayor Interés Territorial)"
    )
    st.markdown("*6 categorías de alta frecuencia de ocurrencia*")

    cols = st.columns(3)
    for i, cat in enumerate(SegmentacionReporte.Categoria.todas()):
        with cols[i % 3]:
            st.markdown(
                f"""
            <div class="category-card" style="border-left-color: #E53935; background: #FFF3E0;">
                <b>{cat["icono"]} {cat["nombre"]}</b><br>
                <small>{cat["descripcion"]}</small>
            </div>
            """,
                unsafe_allow_html=True,
            )

    st.markdown("---")
    st.subheader("📋 2. Tipo de Reporte")

    tipo_options = {
        "rapido": "🎯 Panel de Acceso Directo (6 categorías principales)",
        "convivencia": "⚖️ Incidentes de Convivencia (Ley 1801/2016)",
        "delito": "⚖️ Delitos de Bajo/Mediano Impacto (Ley 599/2000)",
    }

    tipo_reporte = st.selectbox(
        "Seleccione el tipo de reporte *",
        list(tipo_options.keys()),
        format_func=lambda x: tipo_options[x],
        index=list(tipo_options.keys()).index(st.session_state.tipo_reporte),
    )

    if tipo_reporte != st.session_state.tipo_reporte:
        st.session_state.tipo_reporte = tipo_reporte
        if tipo_reporte == "rapido":
            st.session_state.report_category = SegmentacionReporte.Categoria.todas()[0][
                "id"
            ]
        elif tipo_reporte == "convivencia":
            st.session_state.report_category = SegmentacionReporte.Convivencia.todos()[
                0
            ]["id"]
        else:
            st.session_state.report_category = SegmentacionReporte.Delitos.todos()[0][
                "id"
            ]
        st.rerun()

    st.markdown("---")
    st.subheader("📋 3. Categoría del Incidente")

    if tipo_reporte == "rapido":
        cats = SegmentacionReporte.Categoria.todas()
        category_ids = [c["id"] for c in cats]
        category_labels = [f"{c['icono']} {c['nombre']}" for c in cats]
        category_map = dict(zip(category_ids, category_labels))
        category = st.selectbox(
            "Seleccione la categoría *",
            category_ids,
            format_func=lambda x: category_map.get(x, x),
        )
    elif tipo_reporte == "convivencia":
        cats = SegmentacionReporte.Convivencia.todos()
        category_ids = [c["id"] for c in cats]
        category_labels = [f"{c['icono']} {c['nombre']}" for c in cats]
        category_map = dict(zip(category_ids, category_labels))
        category = st.selectbox(
            "Seleccione el tipo de incidente *",
            category_ids,
            format_func=lambda x: category_map.get(x, x),
        )
    else:
        cats = SegmentacionReporte.Delitos.todos()
        category_ids = [c["id"] for c in cats]
        category_labels = [f"{c['icono']} {c['nombre']}" for c in cats]
        category_map = dict(zip(category_ids, category_labels))
        category = st.selectbox(
            "Seleccione el tipo de delito *",
            category_ids,
            format_func=lambda x: category_map.get(x, x),
        )

    with st.form("report_form", clear_on_submit=False):
        title = st.text_input(
            "Título del Incidente *", placeholder="Descripción breve del incidente"
        )

        col1, col2 = st.columns(2)
        with col1:
            reporter = st.text_input(
                "Reportado por *",
                placeholder="Nombre del reportante (o 'Anónimo' para reportes comunitarios)",
            )
            contact = st.text_input(
                "Contacto", placeholder="Teléfono o email (opcional si es anónimo)"
            )

        with col2:
            severity = st.selectbox(
                "Severidad *",
                [s["id"] for s in SegmentacionReporte.Severidad.todas()],
                format_func=lambda x: (
                    f"{[s['icono'] for s in SegmentacionReporte.Severidad.todas() if s['id'] == x][0]} {[s['nombre'] for s in SegmentacionReporte.Severidad.todas() if s['id'] == x][0]}"
                ),
            )
            fuente = st.selectbox(
                "Fuente del Reporte",
                [f["id"] for f in SegmentacionReporte.Fuente.todas()],
                format_func=lambda x: (
                    f"{[f['icono'] for f in SegmentacionReporte.Fuente.todas() if f['id'] == x][0]} {[f['nombre'] for f in SegmentacionReporte.Fuente.todas() if f['id'] == x][0]}"
                ),
            )

        description = st.text_area(
            "Descripción Detallada *",
            height=120,
            placeholder="Describa el incidente con detalle...",
        )

        st.markdown("---")
        st.subheader("📍 4. Ubicación del Incidente (Georreferenciación Automática)")

        method = st.radio(
            "Método de ubicación:",
            [
                "📍 Seleccionar zona",
                "🔍 Buscar dirección",
                "📡 Mi ubicación (IP)",
                "🗺️ Seleccionar en mapa",
            ],
            horizontal=True,
        )

        location_data = {}

        if method == "📍 Seleccionar zona":
            st.markdown("##### 🏘️ Zonas de Medellín y Área Metropolitana")

            zona_list = list(ZONAS_MEDELLIN.items())
            zona_options = [("", "Seleccionar zona...")] + [
                (k, v["nombre"]) for k, v in zona_list
            ]
            zona_ids = [z[0] for z in zona_options]
            zona_labels = [z[1] for z in zona_options]
            zona_map = dict(zip(zona_ids, zona_labels))

            selected_zona = st.selectbox(
                "Seleccione una zona:",
                zona_ids,
                format_func=lambda x: zona_map.get(x, ""),
            )

            if selected_zona:
                zona = ZONAS_MEDELLIN[selected_zona]
                st.session_state.map_center = [zona["lat"], zona["lon"]]
                st.markdown(f"**Zona seleccionada:** {zona['nombre']}")
                st.markdown(f"**Comunas:** {', '.join(zona.get('comunas', []))}")

                col_map, col_info = st.columns([2, 1])
                with col_map:
                    m = create_map([], st.session_state.map_center, zoom=14)
                    clicked = st_folium(
                        m,
                        width=500,
                        height=350,
                        key="zona_map",
                        returned_objects=["last_clicked"],
                    )

                with col_info:
                    st.markdown("##### 📍 Coordenadas")
                    lat = zona["lat"]
                    lon = zona["lon"]

                    if clicked.get("last_clicked"):
                        lat, lon = (
                            clicked["last_clicked"]["lat"],
                            clicked["last_clicked"]["lng"],
                        )

                    st.write(f"**Latitud:** {lat:.6f}")
                    st.write(f"**Longitud:** {lon:.6f}")

                    lat = st.number_input(
                        "Latitud", value=lat, format="%.6f", key="lat_input"
                    )
                    lon = st.number_input(
                        "Longitud", value=lon, format="%.6f", key="lon_input"
                    )

                if st.form_submit_button("✅ Confirmar ubicación"):
                    loc = geo_service.reverse_geocode(lat, lon)
                    if loc:
                        location_data = {**loc, "latitude": lat, "longitude": lon}
                        location_data["zona"] = zona["nombre"]
                        st.session_state.pending_location = location_data
                        st.session_state.location_confirmed = True
                        st.success(f"✅ Ubicación confirmada: {zona['nombre']}")

        elif method == "🔍 Buscar dirección":
            addr = st.text_input(
                "Dirección:", placeholder="Ej: Cra 43A #1-50, Medellín"
            )
            if addr and st.form_submit_button("🔍 Buscar en Geoapify"):
                with st.spinner("Consultando API de Geoapify..."):
                    loc = geo_service.geocode(addr)
                    if loc:
                        location_data = loc
                        st.session_state.pending_location = loc
                        st.session_state.location_confirmed = True
                        st.success(f"✅ {loc.get('address', '')}")
                        st.session_state.map_center = [
                            loc.get("latitude"),
                            loc.get("longitude"),
                        ]
                    else:
                        st.error("No se encontró la dirección")

        elif method == "📡 Mi ubicación (IP)":
            if st.form_submit_button("📍 Obtener mi ubicación"):
                with st.spinner("Obteniendo ubicación..."):
                    loc = geo_service.get_ip_location()
                    if loc:
                        location_data = loc
                        st.session_state.pending_location = loc
                        st.session_state.location_confirmed = True
                        st.success(
                            f"✅ {loc.get('city', '')}, {loc.get('country', '')}"
                        )
                        st.session_state.map_center = [
                            loc.get("latitude"),
                            loc.get("longitude"),
                        ]

        elif method == "🗺️ Seleccionar en mapa":
            m = create_map([], st.session_state.map_center)
            clicked = st_folium(
                m,
                width=700,
                height=400,
                key="sel_map",
                returned_objects=["last_clicked"],
            )

            col_lat, col_lon = st.columns(2)
            with col_lat:
                lat = st.number_input("Latitud", value=6.2442, format="%.6f")
            with col_lon:
                lon = st.number_input("Longitud", value=-75.5812, format="%.6f")

            if clicked.get("last_clicked"):
                lat, lon = (
                    clicked["last_clicked"]["lat"],
                    clicked["last_clicked"]["lng"],
                )

            if st.form_submit_button("✅ Confirmar ubicación"):
                loc = geo_service.reverse_geocode(lat, lon)
                if loc:
                    location_data = {**loc, "latitude": lat, "longitude": lon}
                    st.session_state.pending_location = location_data
                    st.session_state.location_confirmed = True

        if st.session_state.location_confirmed and st.session_state.pending_location:
            loc = st.session_state.pending_location
            zona_display = loc.get("zona", "")
            st.markdown(
                f"""
            <div style="background: #E3F2FD; padding: 15px; border-radius: 10px; border-left: 4px solid #1565C0;">
                <b>📍 Ubicación Confirmada</b><br>
                {loc.get("address", "N/A")}<br>
                <small>🏘️ {zona_display} | {loc.get("city", "")} | Lat: {loc.get("latitude", 0):.6f}, Lon: {loc.get("longitude", 0):.6f}</small>
            </div>
            """,
                unsafe_allow_html=True,
            )

        location_data = {}

        if method == "📍 Seleccionar zona":
            st.markdown("##### 🏘️ Zonas de Medellín y Área Metropolitana")

            zona_cols = st.columns(3)
            zona_keys = list(ZONAS_MEDELLIN.keys())

            for i, zona_id in enumerate(zona_keys[:6]):
                zona = ZONAS_MEDELLIN[zona_id]
                with zona_cols[i % 3]:
                    if st.button(
                        f"🏠 {zona['nombre']}",
                        key=f"zona_{zona_id}",
                        use_container_width=True,
                    ):
                        st.session_state.map_center = [zona["lat"], zona["lon"]]

            for i, zona_id in enumerate(zona_keys[6:12]):
                zona = ZONAS_MEDELLIN[zona_id]
                with zona_cols[i % 3]:
                    if st.button(
                        f"🏢 {zona['nombre']}",
                        key=f"zona_{zona_id}",
                        use_container_width=True,
                    ):
                        st.session_state.map_center = [zona["lat"], zona["lon"]]

            for i, zona_id in enumerate(zona_keys[12:18]):
                zona = ZONAS_MEDELLIN[zona_id]
                with zona_cols[i % 3]:
                    if st.button(
                        f"🏙️ {zona['nombre']}",
                        key=f"zona_{zona_id}",
                        use_container_width=True,
                    ):
                        st.session_state.map_center = [zona["lat"], zona["lon"]]

            st.markdown("##### 🗺️ Mapa de la Zona")
            m = create_map([], st.session_state.map_center, zoom=14)
            clicked = st_folium(
                m,
                width=700,
                height=400,
                key="zona_map",
                returned_objects=["last_clicked"],
            )

            selected_zona = st.selectbox(
                "O seleccione una zona específica:",
                [""] + list(ZONAS_MEDELLIN.keys()),
                format_func=lambda x: (
                    ZONAS_MEDELLIN.get(x, {}).get("nombre", "Seleccionar...")
                    if x
                    else "Seleccionar zona..."
                ),
            )

            if selected_zona:
                zona = ZONAS_MEDELLIN[selected_zona]
                st.session_state.map_center = [zona["lat"], zona["lon"]]
                m = create_map([], st.session_state.map_center, zoom=14)
                clicked = st_folium(
                    m,
                    width=700,
                    height=400,
                    key="zona_map_selected",
                    returned_objects=["last_clicked"],
                )

            col_lat, col_lon = st.columns(2)
            lat = st.session_state.map_center[0]
            lon = st.session_state.map_center[1]

            if clicked.get("last_clicked"):
                lat, lon = (
                    clicked["last_clicked"]["lat"],
                    clicked["last_clicked"]["lng"],
                )

            with col_lat:
                lat = st.number_input(
                    "Latitud", value=lat, format="%.6f", key="lat_input"
                )
            with col_lon:
                lon = st.number_input(
                    "Longitud", value=lon, format="%.6f", key="lon_input"
                )

            if st.form_submit_button("✅ Confirmar ubicación"):
                loc = geo_service.reverse_geocode(lat, lon)
                if loc:
                    location_data = {**loc, "latitude": lat, "longitude": lon}
                    zona_nombre = next(
                        (
                            z["nombre"]
                            for z_id, z in ZONAS_MEDELLIN.items()
                            if abs(z["lat"] - lat) < 0.01 and abs(z["lon"] - lon) < 0.01
                        ),
                        "Medellín",
                    )
                    location_data["zona"] = zona_nombre
                    st.session_state.pending_location = location_data
                    st.session_state.location_confirmed = True
                    st.success(f"✅ Ubicación confirmada: {zona_nombre}")

        elif method == "🔍 Buscar dirección":
            addr = st.text_input(
                "Dirección:", placeholder="Ej: Cra 43A #1-50, Medellín"
            )
            if addr and st.form_submit_button("🔍 Buscar en Geoapify"):
                with st.spinner("Consultando API de Geoapify..."):
                    loc = geo_service.geocode(addr)
                    if loc:
                        location_data = loc
                        st.session_state.pending_location = loc
                        st.session_state.location_confirmed = True
                        st.success(f"✅ {loc.get('address', '')}")
                        st.session_state.map_center = [
                            loc.get("latitude"),
                            loc.get("longitude"),
                        ]
                    else:
                        st.error("No se encontró la dirección")

        elif method == "📡 Mi ubicación (IP)":
            if st.form_submit_button("📍 Obtener mi ubicación"):
                with st.spinner("Obteniendo ubicación..."):
                    loc = geo_service.get_ip_location()
                    if loc:
                        location_data = loc
                        st.session_state.pending_location = loc
                        st.session_state.location_confirmed = True
                        st.success(
                            f"✅ {loc.get('city', '')}, {loc.get('country', '')}"
                        )
                        st.session_state.map_center = [
                            loc.get("latitude"),
                            loc.get("longitude"),
                        ]

        elif method == "🗺️ Seleccionar en mapa":
            m = create_map([], st.session_state.map_center)
            clicked = st_folium(
                m,
                width=700,
                height=400,
                key="sel_map",
                returned_objects=["last_clicked"],
            )

            col_lat, col_lon = st.columns(2)
            with col_lat:
                lat = st.number_input("Latitud", value=6.2442, format="%.6f")
            with col_lon:
                lon = st.number_input("Longitud", value=-75.5812, format="%.6f")

            if clicked.get("last_clicked"):
                lat, lon = (
                    clicked["last_clicked"]["lat"],
                    clicked["last_clicked"]["lng"],
                )

            if st.form_submit_button("✅ Confirmar ubicación"):
                loc = geo_service.reverse_geocode(lat, lon)
                if loc:
                    location_data = {**loc, "latitude": lat, "longitude": lon}
                    st.session_state.pending_location = location_data
                    st.session_state.location_confirmed = True

        if st.session_state.location_confirmed and st.session_state.pending_location:
            loc = st.session_state.pending_location
            zona_display = loc.get("zona", "")
            st.markdown(
                f"""
            <div style="background: #E3F2FD; padding: 15px; border-radius: 10px; border-left: 4px solid #1565C0;">
                <b>📍 Ubicación Confirmada</b><br>
                {loc.get("address", "N/A")}<br>
                <small>🏘️ {zona_display} | {loc.get("city", "")} | Lat: {loc.get("latitude", 0):.6f}, Lon: {loc.get("longitude", 0):.6f}</small>
            </div>
            """,
                unsafe_allow_html=True,
            )

        st.markdown("---")
        st.markdown(
            "**⏱️ Timestamp automático y georreferenciación se asignarán al enviar el reporte**"
        )

        submitted = st.form_submit_button(
            "📨 Enviar Reporte", type="primary", use_container_width=True
        )

        if submitted:
            if not title or not description or not reporter:
                st.error("⚠️ Complete todos los campos requeridos (*)")
            elif not st.session_state.location_confirmed:
                st.error("⚠️ Seleccione una ubicación")
            else:
                tipo_ley = None
                if tipo_reporte == "convivencia":
                    tipo_ley = "Ley 1801/2016"
                elif tipo_reporte == "delito":
                    tipo_ley = "Ley 599/2000"

                incident = {
                    "title": title,
                    "description": description,
                    "category": category,
                    "tipo_reporte": tipo_reporte,
                    "ley": tipo_ley,
                    "severity": severity,
                    "fuente": fuente,
                    "location": st.session_state.pending_location,
                    "reporter_name": reporter,
                    "reporter_contact": contact,
                    "status": "recibido",
                    "timestamp": datetime.now().isoformat(),
                }

                created = storage.create(incident)
                st.session_state.pending_location = None
                st.session_state.location_confirmed = False

                st.success(f"✅ Reporte creado exitosamente!")
                st.info(f"📋 ID del reporte: `{created['id']}`")
                st.info(
                    f"📜 Tipo: {tipo_options.get(tipo_reporte, '')} | Ley: {tipo_ley}"
                )
                st.balloons()


def page_map():
    st.title("🗺️ Mapa Global de Incidentes")
    st.markdown("Visualización geoespacial de todos los reportes")
    st.markdown("*Basado en: SEGMENTACIÓN ESTRATÉGICA DE LAS VARIABLES DE REPORTE*")

    all_categories = get_all_categories()
    cat_options = ["Todas"] + [c["id"] for c in all_categories]
    cat_labels = ["Todas"] + [f"{c['icono']} {c['nombre']}" for c in all_categories]
    cat_dict = dict(zip(cat_options, cat_labels))

    col1, col2, col3 = st.columns(3)
    with col1:
        f_cat = st.selectbox(
            "Categoría", cat_options, format_func=lambda x: cat_dict.get(x, x)
        )
    with col2:
        f_sev = st.selectbox(
            "Severidad",
            ["Todas"] + [s["id"] for s in SegmentacionReporte.Severidad.todas()],
        )
    with col3:
        f_stat = st.selectbox(
            "Estado", ["Todos"] + [e["id"] for e in SegmentacionReporte.Estado.todos()]
        )

    incidents = storage.get_all()

    if f_cat != "Todas":
        incidents = [i for i in incidents if i.get("category") == f_cat]
    if f_sev != "Todas":
        incidents = [i for i in incidents if i.get("severity") == f_sev]
    if f_stat != "Todos":
        incidents = [i for i in incidents if i.get("status") == f_stat]

    st.markdown(f"**Total de incidentes:** {len(incidents)}")

    if incidents:
        m = create_map(incidents, st.session_state.map_center, zoom=11)
        st_folium(m, width=1100, height=650, key="full_map")
    else:
        m = create_map([], DEFAULT_MAP_CENTER)
        st_folium(m, width=1100, height=650)


def page_list():
    st.title("📋 Todos los Reportes")
    st.markdown("Gestión completa de incidentes")

    incidents = storage.get_all()
    st.markdown(f"**Total:** {len(incidents)} reportes")

    if not incidents:
        st.info("No hay reportes")
        return

    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        f_cat = st.selectbox(
            "Filtrar categoría",
            ["Todas"] + [c["id"] for c in SegmentacionReporte.Categoria.todas()],
        )
    with col2:
        f_stat = st.selectbox(
            "Filtrar estado",
            ["Todos"] + [e["id"] for e in SegmentacionReporte.Estado.todos()],
        )

    if f_cat != "Todas":
        incidents = [i for i in incidents if i.get("category") == f_cat]
    if f_stat != "Todos":
        incidents = [i for i in incidents if i.get("status") == f_stat]

    for i, inc in enumerate(incidents):
        cat, sev = inc.get("category", "seguridad"), inc.get("severity", "bajo")

        with st.expander(
            f"{CATEGORY_EMOJI.get(cat, '📌')} {inc.get('title', '')} | :{SEVERITY_COLORS.get(sev, 'blue')}[{sev.upper()}]"
        ):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(
                    f"**📁 Categoría:** {inc.get('subcategoria', inc.get('category', ''))}"
                )
                st.markdown(f"**⚠️ Severidad:** {inc.get('severity', '')}")
            with col2:
                st.markdown(f"**🎯 Prioridad:** {inc.get('priority', '')}")
                st.markdown(f"**📊 Estado:** {inc.get('status', '')}")
            with col3:
                st.markdown(f"**👤 Reportante:** {inc.get('reporter_name', '')}")
                st.markdown(f"**📅 Fecha:** {inc.get('created_at', '')[:16]}")

            st.markdown(f"**📝 Descripción:** {inc.get('description', '')}")

            loc = inc.get("location", {})
            st.markdown(f"**📍 Ubicación:** {loc.get('address', 'N/A')}")
            st.markdown(
                f"**🗺️ Coordenadas:** ({loc.get('latitude', 0):.6f}, {loc.get('longitude', 0):.6f})"
            )

            col_upd, col_del = st.columns(2)

            with col_upd:
                new_status = st.selectbox(
                    "Cambiar Estado",
                    [e["id"] for e in SegmentacionReporte.Estado.todos()],
                    index=[e["id"] for e in SegmentacionReporte.Estado.todos()].index(
                        inc.get("status", "recibido")
                    )
                    if inc.get("status", "recibido")
                    in [e["id"] for e in SegmentacionReporte.Estado.todos()]
                    else 0,
                    key=f"stat_{inc.get('id')}_{i}",
                )
                if new_status != inc.get("status"):
                    if st.button(f"✅ Actualizar", key=f"btn_{inc.get('id')}_{i}"):
                        storage.update(inc.get("id"), {"status": new_status})
                        st.success("Estado actualizado")
                        st.rerun()

            with col_del:
                if st.button(f"🗑️ Eliminar", key=f"del_{inc.get('id')}_{i}"):
                    storage.delete(inc.get("id"))
                    st.success("Eliminado")
                    st.rerun()


def page_stats():
    st.title("📈 Analytics")
    st.markdown("Análisis de datos de incidentes")

    stats = storage.get_stats()
    render_stats(stats)


def page_settings():
    st.title("⚙️ Configuración")

    st.subheader("🗺️ API de Geoapify")

    col1, col2 = st.columns([2, 1])
    with col1:
        st.text_input("API Key", value=GEOAPIFY_API_KEY, type="password")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Probar Conexión"):
            with st.spinner("Probando..."):
                if geo_service.test_connection():
                    st.success("✅ Conexión exitosa con Geoapify API")
                else:
                    st.error("❌ Error de conexión")

    st.markdown("---")
    st.subheader("ℹ️ Información del Sistema")

    st.markdown(f"""
    **SAFE GeoReport v2.0.0**
    
    | Configuración | Valor |
    |--------------|-------|
    | API Key | `{GEOAPIFY_API_KEY}` |
    | URL Base | `{GEOAPIFY_BASE_URL}` |
    | Tiles | Geoapify Carto |
    | Provider | ACTIVO |
    
    **Segmentación Estratégica (Basada en: SEGMENTACIÓN ESTRATÉGICA DE LAS VARIABLES DE REPORTE):**
    
    **1. Panel de Acceso Directo (Variables de Mayor Interés Territorial):** {len(SegmentacionReporte.Categoria.todas())}
    - Hurto a Personas, Hurto a Comercios, Hurto a Vehículos
    - Hurto a Residencias, Violencia Intrafamiliar, Extorsión
    
    **2. Incidentes de Convivencia (Ley 1801/2016):** {len(SegmentacionReporte.Convivencia.todos())}
    - Alteraciones al orden público, Extorsión menor, Hurto a comercios
    - Hurto a personas, Hurto a residencias, Hurto a vehículos
    - Lesiones personales, Riñas callejeras, Ruido excesivo
    - Vandalismo, Violencia intrafamiliar, Otro
    
    **3. Delitos de Bajo/Mediano Impacto (Ley 599/2000):** {len(SegmentacionReporte.Delitos.todos())}
    - Delitos sexuales menores, Extorsión, Hurto a personas
    - Hurto a residencias, Hurto a vehículos/motocicletas
    - Lesiones personales, Violencia de género, Violencia intrafamiliar
    - Otro
    
    **Niveles de Severidad:** {len(SegmentacionReporte.Severidad.todas())}
    **Estados:** {len(SegmentacionReporte.Estado.todos())}
    **Fuentes:** {len(SegmentacionReporte.Fuente.todas())}
    
    ---
    🛡️ SAFE Inteligencia Segura - Siempre Activa
    """)


# =============================================================================
# MAIN
# =============================================================================


def main():
    init_session()
    render_header()

    choice = render_sidebar()

    pages = {
        "🏠 Dashboard": page_dashboard,
        "📝 Nuevo Reporte": page_report,
        "🗺️ Mapa Global": page_map,
        "📋 Todos los Reportes": page_list,
        "📈 Analytics": page_stats,
        "⚙️ Configuración": page_settings,
    }

    pages[choice]()


if __name__ == "__main__":
    main()
