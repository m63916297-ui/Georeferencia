import streamlit as st
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
from folium.plugins import MarkerCluster
import folium
from .models import Incident, SeverityLevel, IncidentCategory


CATEGORY_ICONS = {
    "seguridad": "🔒",
    "infraestructura": "🏗️",
    "servicios": "⚙️",
    "ambiental": "🌿",
    "transito": "🚗",
    "otro": "📌",
}

SEVERITY_COLORS = {
    "bajo": "green",
    "medio": "orange",
    "alto": "red",
    "critico": "darkred",
}

STATUS_LABELS = {
    "pendiente": "⏳ Pendiente",
    "en_proceso": "🔄 En Proceso",
    "resuelto": "✅ Resuelto",
    "cerrado": "🔒 Cerrado",
}


def init_session_state():
    if "incidents" not in st.session_state:
        st.session_state.incidents = []
    if "current_location" not in st.session_state:
        st.session_state.current_location = None
    if "map_center" not in st.session_state:
        st.session_state.map_center = [4.5709, -74.2973]
    if "filters" not in st.session_state:
        st.session_state.filters = {}


def render_header():
    st.set_page_config(
        page_title="GeoReport - Sistema de Gestión de Incidentes",
        page_icon="📍",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown(
        """
    <style>
    .main-header {
        background: linear-gradient(90deg, #1E88E5, #1565C0);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .main-header h1 {
        color: white;
        margin: 0;
        padding: 0;
    }
    .main-header p {
        color: #E3F2FD;
        margin: 5px 0 0 0;
    }
    .provider-badge {
        background-color: #4CAF50;
        color: white;
        padding: 5px 10px;
        border-radius: 5px;
        font-size: 12px;
        font-weight: bold;
    }
    .stat-card {
        background-color: #f5f5f5;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        border-left: 4px solid #1E88E5;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(
            """
        <div class="main-header">
            <h1>📍 GeoReport Provider</h1>
            <p>Sistema de Gestión y Reporte de Incidentes Georreferenciados</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            '<span class="provider-badge">🏢 PROVIDER ACTIVO</span>',
            unsafe_allow_html=True,
        )


def render_sidebar():
    st.sidebar.title("📊 Navegación")

    menu_options = [
        "🏠 Dashboard",
        "📝 Reportar Incidente",
        "🗺️ Ver Mapa de Incidentes",
        "📋 Lista de Incidentes",
        "📈 Estadísticas",
        "⚙️ Configuración",
    ]

    choice = st.sidebar.radio("Menú", menu_options)

    st.sidebar.markdown("---")
    st.sidebar.markdown("### ℹ️ Información")
    st.sidebar.info(
        """
        **GeoReport Provider**
        
        Versión: 1.0.0
        
        Powered by Geoapify API
        
        © 2026 GeoReport
        """
    )

    return choice


def create_incident_map(incidents: List[Incident], center: List[float] = None):
    if center is None:
        center = [4.5709, -74.2973]

    m = folium.Map(location=center, zoom_start=10, tiles="cartodbpositron")

    if not incidents:
        return m

    for incident in incidents:
        if incident.location and "latitude" in incident.location:
            popup_content = f"""
            <b>{incident.title}</b><br>
            <i>{CATEGORY_ICONS.get(incident.category, "📌")} {incident.category.upper()}</i><br>
            <b>Severidad:</b> {incident.severity}<br>
            <b>Estado:</b> {incident.status}<br>
            <hr>
            <small>{incident.description[:100]}...</small>
            """

            folium.Marker(
                location=[
                    incident.location["latitude"],
                    incident.location["longitude"],
                ],
                popup=folium.Popup(popup_content, max_width=300),
                icon=folium.Icon(
                    color=SEVERITY_COLORS.get(incident.severity, "blue"),
                    icon=CATEGORY_ICONS.get(incident.category, "info-sign"),
                    prefix="fa",
                ),
            ).add_to(m)

    return m


def render_incident_card(incident: Incident):
    severity_color = SEVERITY_COLORS.get(incident.severity, "blue")

    with st.expander(f"{CATEGORY_ICONS.get(incident.category, '📌')} {incident.title}"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Categoría:** {incident.category}")
            st.markdown(
                f"**Severidad:** :{severity_color}[{incident.severity.upper()}]"
            )
            st.markdown(
                f"**Estado:** {STATUS_LABELS.get(incident.status, incident.status)}"
            )
        with col2:
            st.markdown(f"**Reportero:** {incident.reporter_name}")
            st.markdown(f"**Contacto:** {incident.reporter_contact}")
            st.markdown(
                f"**Fecha:** {datetime.fromisoformat(incident.created_at).strftime('%Y-%m-%d %H:%M')}"
            )

        st.markdown("---")
        st.markdown(f"**Descripción:** {incident.description}")

        if incident.location:
            st.markdown(f"**Dirección:** {incident.location.get('address', 'N/A')}")
            st.markdown(
                f"**Coordenadas:** ({incident.location.get('latitude', 0):.4f}, {incident.location.get('longitude', 0):.4f})"
            )


def get_category_options():
    return [c.value for c in IncidentCategory]


def get_severity_options():
    return [s.value for s in SeverityLevel]


def get_status_options():
    return ["pendiente", "en_proceso", "resuelto", "cerrado"]


def render_statistics(stats: Dict[str, Any]):
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Incidentes", stats.get("total", 0))
    with col2:
        pend = stats.get("by_status", {}).get("pendiente", 0)
        st.metric("Pendientes", pend)
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
