import streamlit as st
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional


GEOAPIFY_API_KEY = "b4be52d95c1543b99864371eb4562a37"

CATEGORY_EMOJI = {
    "hurto_personas": "🎯",
    "hurto_comercios": "🏪",
    "hurto_vehiculos": "🚗",
    "hurto_residencias": "🏠",
    "violencia_intrafamiliar": "⚠️",
    "extorsion": "💰",
    "alteraciones_orden": "📢",
    "extorsion_menor": "💵",
    "lesiones_personales": "🩹",
    "rinas_callejeras": "👊",
    "ruido_excesivo": "🔊",
    "vandalismo": "🔨",
    "otro_convivencia": "📝",
    "delitos_sexuales": "🚫",
    "violencia_genero": "⚧️",
    "otro_delito": "📝",
}

SEVERITY_COLORS = {
    "bajo": "green",
    "medio": "orange",
    "alto": "red",
    "critico": "darkred",
}

STATUS_LABELS = {
    "recibido": "📥 Recibido",
    "validando": "🔍 Validando",
    "asignado": "👤 Asignado",
    "en_proceso": "⚙️ En Proceso",
    "resuelto": "✅ Resuelto",
    "cerrado": "🔒 Cerrado",
    "rechazado": "❌ Rechazado",
}

DEFAULT_MAP_CENTER = [6.2442, -75.5812]
DEFAULT_ZOOM_START = 12


def init_session_state():
    if "incidents" not in st.session_state:
        st.session_state.incidents = []
    if "current_location" not in st.session_state:
        st.session_state.current_location = None
    if "map_center" not in st.session_state:
        st.session_state.map_center = DEFAULT_MAP_CENTER.copy()
    if "filters" not in st.session_state:
        st.session_state.filters = {}
    if "pending_location" not in st.session_state:
        st.session_state.pending_location = None
    if "location_confirmed" not in st.session_state:
        st.session_state.location_confirmed = False
    if "navigate_to" not in st.session_state:
        st.session_state.navigate_to = None
    if "last_incident_id" not in st.session_state:
        st.session_state.last_incident_id = None


def get_geoapify_tiles(api_key: str = None) -> str:
    if api_key is None:
        api_key = GEOAPIFY_API_KEY
    return f"https://maps.geoapify.com/v1/tile/carto/{{z}}/{{x}}/{{y}}.png?apiKey={api_key}"


def get_category_options():
    cats = []
    cats.extend(
        [
            {"id": "hurto_personas", "nombre": "Hurto a Personas"},
            {"id": "hurto_comercios", "nombre": "Hurto a Comercios"},
            {"id": "hurto_vehiculos", "nombre": "Hurto a Vehículos"},
            {"id": "hurto_residencias", "nombre": "Hurto a Residencias"},
            {"id": "violencia_intrafamiliar", "nombre": "Violencia Intrafamiliar"},
            {"id": "extorsion", "nombre": "Extorsión"},
        ]
    )
    cats.extend(
        [
            {"id": "alteraciones_orden", "nombre": "Alteraciones al Orden Público"},
            {"id": "extorsion_menor", "nombre": "Extorsión Menor"},
            {"id": "lesiones_personales", "nombre": "Lesiones Personales"},
            {"id": "rinas_callejeras", "nombre": "Riñas Callejeras"},
            {"id": "ruido_excesivo", "nombre": "Ruido Excesivo"},
            {"id": "vandalismo", "nombre": "Vandalismo"},
            {"id": "otro_convivencia", "nombre": "Otro Convivencia"},
        ]
    )
    cats.extend(
        [
            {"id": "delitos_sexuales", "nombre": "Delitos Sexuales Menores"},
            {"id": "violencia_genero", "nombre": "Violencia de Género"},
            {"id": "otro_delito", "nombre": "Otro Delito"},
        ]
    )
    return cats


def get_severity_options():
    return [
        {"id": "critico", "nombre": "Crítico"},
        {"id": "alto", "nombre": "Alto"},
        {"id": "medio", "nombre": "Medio"},
        {"id": "bajo", "nombre": "Bajo"},
    ]


def get_status_options():
    return [
        "recibido",
        "validando",
        "asignado",
        "en_proceso",
        "resuelto",
        "cerrado",
        "rechazado",
    ]


def render_statistics(stats: Dict[str, Any]):
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Incidentes", stats.get("total", 0))
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

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Por Categoría")
        cat_data = stats.get("by_category", {})
        if cat_data:
            df_cat = pd.DataFrame(
                list(cat_data.items()), columns=["Categoría", "Cantidad"]
            )
            st.bar_chart(df_cat.set_index("Categoría"))
        else:
            st.info("No hay datos disponibles")

    with col2:
        st.subheader("Por Severidad")
        sev_data = stats.get("by_severity", {})
        if sev_data:
            df_sev = pd.DataFrame(
                list(sev_data.items()), columns=["Severidad", "Cantidad"]
            )
            st.bar_chart(df_sev.set_index("Severidad"))
        else:
            st.info("No hay datos disponibles")
