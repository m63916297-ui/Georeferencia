import streamlit as st
from streamlit_folium import st_folium
from datetime import datetime
from typing import Optional

from .models import Incident, ReportFilters
from .storage import JSONStorage
from .geo_service import GeoapifyService
from .utils import (
    init_session_state,
    render_header,
    render_sidebar,
    create_incident_map,
    render_incident_card,
    get_category_options,
    get_severity_options,
    get_status_options,
    render_statistics,
    CATEGORY_ICONS,
    SEVERITY_COLORS,
)


storage = JSONStorage("georeferencia/data/incidents.json")
geo_service = GeoapifyService()


def page_dashboard():
    st.title("📊 Dashboard")
    st.markdown("Vista general del sistema de gestión de incidentes")

    stats = storage.get_statistics()
    render_statistics(stats)

    st.markdown("---")
    st.subheader("🗺️ Vista Rápida del Mapa")

    incidents = storage.get_all_incidents()
    if incidents:
        map_obj = create_incident_map(incidents, st.session_state.map_center)
        st_folium(map_obj, width=800, height=500)
    else:
        st.info("No hay incidentes registrados. ¡Sé el primero en reportar uno!")


def page_report_incident():
    st.title("📝 Reportar Nuevo Incidente")
    st.markdown("Complete el formulario para reportar un nuevo incidente")

    with st.form("incident_form"):
        col1, col2 = st.columns(2)

        with col1:
            title = st.text_input(
                "Título del Incidente", placeholder="Ej: Bache en calle principal"
            )
            category = st.selectbox("Categoría", get_category_options())
            severity = st.selectbox("Severidad", get_severity_options())

        with col2:
            reporter_name = st.text_input(
                "Nombre del Reportador", placeholder="Su nombre"
            )
            reporter_contact = st.text_input("Contacto", placeholder="Teléfono o email")

        description = st.text_area(
            "Descripción Detallada",
            height=150,
            placeholder="Describa el incidente con el mayor detalle posible...",
        )

        st.markdown("---")
        st.subheader("📍 Ubicación")

        location_method = st.radio(
            "Método de ubicación",
            ["Buscar dirección", "Usar mi ubicación actual", "Seleccionar en mapa"],
        )

        location_data = {}

        if location_method == "Buscar dirección":
            address = st.text_input(
                "Dirección", placeholder="Ingrese la dirección del incidente"
            )
            if address and st.form_submit_button("🔍 Buscar en mapa"):
                with st.spinner("Buscando ubicación..."):
                    location = geo_service.geocode(address)
                    if location:
                        location_data = {
                            "latitude": location.latitude,
                            "longitude": location.longitude,
                            "address": location.address,
                            "city": location.city,
                            "country": location.country,
                            "postal_code": location.postal_code,
                        }
                        st.success(f"✓ Ubicación encontrada: {location.address}")
                        st.session_state.map_center = [
                            location.latitude,
                            location.longitude,
                        ]
                    else:
                        st.error("No se pudo encontrar la ubicación")

        elif location_method == "Usar mi ubicación actual":
            if st.form_submit_button("📍 Obtener mi ubicación"):
                location = geo_service.get_ip_location()
                if location:
                    location_data = {
                        "latitude": location.latitude,
                        "longitude": location.longitude,
                        "address": location.address,
                        "city": location.city,
                        "country": location.country,
                    }
                    st.success(
                        f"✓ Ubicación obtenida: {location.city}, {location.country}"
                    )
                    st.session_state.map_center = [
                        location.latitude,
                        location.longitude,
                    ]
                else:
                    st.error("No se pudo obtener la ubicación")

        elif location_method == "Seleccionar en mapa":
            st.info("Haga clic en el mapa para seleccionar la ubicación")
            map_obj = create_incident_map([], st.session_state.map_center)
            st_folium(map_obj, width=700, height=400, key="selection_map")

            col1, col2 = st.columns(2)
            with col1:
                lat = st.number_input("Latitud", value=4.5709, format="%.6f")
            with col2:
                lon = st.number_input("Longitud", value=-74.2973, format="%.6f")

            if st.form_submit_button("📍 Confirmar ubicación"):
                location = geo_service.reverse_geocode(lat, lon)
                if location:
                    location_data = {
                        "latitude": lat,
                        "longitude": lon,
                        "address": location.address,
                        "city": location.city,
                        "country": location.country,
                        "postal_code": location.postal_code,
                    }
                    st.success(f"✓ Ubicación confirmada: {location.address}")

        submitted = st.form_submit_button("📨 Enviar Reporte", type="primary")

        if submitted:
            if (
                not title
                or not description
                or not reporter_name
                or not reporter_contact
            ):
                st.error("⚠️ Por favor complete todos los campos requeridos")
            else:
                incident = Incident(
                    id="",
                    title=title,
                    description=description,
                    category=category,
                    severity=severity,
                    location=location_data,
                    reporter_name=reporter_name,
                    reporter_contact=reporter_contact,
                    created_at="",
                )

                created = storage.create_incident(incident)
                st.success(f"✅ Incidente reportado exitosamente! ID: {created.id}")

                st.balloons()


def page_map():
    st.title("🗺️ Mapa de Incidentes")
    st.markdown("Visualización geoespacial de todos los incidentes reportados")

    col1, col2 = st.columns([3, 1])

    with col2:
        st.subheader("Filtros")
        filter_category = st.selectbox("Categoría", ["Todas"] + get_category_options())
        filter_severity = st.selectbox("Severidad", ["Todas"] + get_severity_options())
        filter_status = st.selectbox("Estado", ["Todos"] + get_status_options())

    incidents = storage.get_all_incidents()

    if filter_category != "Todas":
        incidents = [i for i in incidents if i.category == filter_category]
    if filter_severity != "Todas":
        incidents = [i for i in incidents if i.severity == filter_severity]
    if filter_status != "Todos":
        incidents = [i for i in incidents if i.status == filter_status]

    st.markdown(f"**Total de incidentes mostrados:** {len(incidents)}")

    if incidents:
        map_obj = create_incident_map(incidents, st.session_state.map_center)
        st_folium(map_obj, width=1000, height=600)
    else:
        st.info("No hay incidentes que coincidan con los filtros seleccionados")


def page_list():
    st.title("📋 Lista de Incidentes")
    st.markdown("Explorar y gestionar todos los incidentes reportados")

    col1, col2, col3 = st.columns(3)

    with col1:
        filter_category = st.selectbox(
            "Filtrar por Categoría", ["Todas"] + get_category_options()
        )
    with col2:
        filter_severity = st.selectbox(
            "Filtrar por Severidad", ["Todas"] + get_severity_options()
        )
    with col3:
        filter_status = st.selectbox(
            "Filtrar por Estado", ["Todos"] + get_status_options()
        )

    incidents = storage.get_all_incidents()

    if filter_category != "Todas":
        incidents = [i for i in incidents if i.category == filter_category]
    if filter_severity != "Todas":
        incidents = [i for i in incidents if i.severity == filter_severity]
    if filter_status != "Todos":
        incidents = [i for i in incidents if i.status == filter_status]

    st.markdown(f"**Total de incidentes:** {len(incidents)}")

    for incident in incidents:
        render_incident_card(incident)

        col1, col2 = st.columns([1, 1])
        with col1:
            new_status = st.selectbox(
                "Cambiar Estado",
                get_status_options(),
                index=get_status_options().index(incident.status)
                if incident.status in get_status_options()
                else 0,
                key=f"status_{incident.id}",
            )
            if new_status != incident.status:
                if st.button(f"Actualizar estado", key=f"btn_{incident.id}"):
                    storage.update_incident(incident.id, {"status": new_status})
                    st.success("Estado actualizado")
                    st.rerun()
        with col2:
            if st.button(f"🗑️ Eliminar", key=f"del_{incident.id}"):
                if storage.delete_incident(incident.id):
                    st.success("Incidente eliminado")
                    st.rerun()


def page_statistics():
    st.title("📈 Estadísticas")
    st.markdown("Análisis detallado de los incidentes reportados")

    stats = storage.get_statistics()
    render_statistics(stats)

    incidents = storage.get_all_incidents()

    if incidents:
        st.markdown("---")
        st.subheader("📋 Historial Reciente")

        recent_incidents = sorted(incidents, key=lambda x: x.created_at, reverse=True)[
            :10
        ]

        for incident in recent_incidents:
            st.markdown(f"""
            **{incident.title}** - {CATEGORY_ICONS.get(incident.category)} {incident.category} - 
            :{SEVERITY_COLORS.get(incident.severity)}[{incident.severity}] - 
            {datetime.fromisoformat(incident.created_at).strftime("%Y-%m-%d %H:%M")}*
            """)


def page_settings():
    st.title("⚙️ Configuración")
    st.markdown("Configuración del sistema")

    st.subheader("API de Geoapify")

    api_key = st.text_input(
        "API Key", value="b4be52d95c1543b99864371eb4562a37", type="password"
    )
    if st.button("Probar conexión"):
        location = geo_service.geocode("Bogotá, Colombia")
        if location:
            st.success(f"✓ Conexión exitosa: {location.city}, {location.country}")
        else:
            st.error("Error de conexión")

    st.markdown("---")
    st.subheader("Acerca de")
    st.markdown("""
    **GeoReport Provider v1.0.0**
    
    Sistema de gestión de incidentes georreferenciados
    
    - Powered by Geoapify API
    - Frontend: Streamlit
    - Almacenamiento: JSON
    """)


def main():
    init_session_state()
    render_header()

    choice = render_sidebar()

    pages = {
        "🏠 Dashboard": page_dashboard,
        "📝 Reportar Incidente": page_report_incident,
        "🗺️ Ver Mapa de Incidentes": page_map,
        "📋 Lista de Incidentes": page_list,
        "📈 Estadísticas": page_statistics,
        "⚙️ Configuración": page_settings,
    }

    pages[choice]()


if __name__ == "__main__":
    main()
