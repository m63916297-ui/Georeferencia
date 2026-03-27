import streamlit as st
from streamlit_folium import st_folium
from datetime import datetime
from typing import Optional, Tuple
import folium

from .models import Incident, ReportFilters
from .storage import JSONStorage
from .geo_service import GeoapifyService
from .utils import (
    init_session_state,
    render_header,
    render_sidebar,
    create_incident_map,
    get_geoapify_tiles,
    render_incident_card,
    get_category_options,
    get_severity_options,
    get_status_options,
    render_statistics,
    CATEGORY_EMOJI,
    SEVERITY_COLORS,
    GEOAPIFY_API_KEY,
    DEFAULT_MAP_CENTER,
)


storage = JSONStorage("georeferencia/data/incidents.json")
geo_service = GeoapifyService(GEOAPIFY_API_KEY)


def page_dashboard():
    st.title("📊 Dashboard")
    st.markdown("### Vista general del sistema de gestión de incidentes")

    stats = storage.get_statistics()
    render_statistics(stats)

    st.markdown("---")
    st.subheader("🗺️ Vista Rápida del Mapa")

    incidents = storage.get_all_incidents()

    col1, col2 = st.columns([3, 1])

    with col1:
        if incidents:
            map_obj = create_incident_map(
                incidents,
                center=st.session_state.get("map_center", DEFAULT_MAP_CENTER),
                api_key=GEOAPIFY_API_KEY,
            )
            st_folium(map_obj, width=800, height=500, key="dashboard_map")
        else:
            m = folium.Map(
                location=DEFAULT_MAP_CENTER,
                zoom_start=10,
                tiles=get_geoapify_tiles(GEOAPIFY_API_KEY),
                attr='&copy; <a href="https://www.geoapify.com/">Geoapify</a>',
            )
            st_folium(m, width=800, height=500)
            st.info("No hay incidentes registrados. ¡Sé el primero en reportar uno!")

    with col2:
        st.markdown("### 📋 Incidentes Recientes")
        recent = sorted(incidents, key=lambda x: x.created_at, reverse=True)[:5]
        for inc in recent:
            severity_color = SEVERITY_COLORS.get(inc.severity, "blue")
            st.markdown(f"""
            **{CATEGORY_EMOJI.get(inc.category, "📌")} {inc.title}**
            - :{severity_color}[{inc.severity}]
            - {inc.status}
            """)


def page_report_incident():
    st.title("📝 Reportar Nuevo Incidente")
    st.markdown("Complete el formulario para reportar un nuevo incidente")

    if "pending_location" not in st.session_state:
        st.session_state.pending_location = None
    if "location_confirmed" not in st.session_state:
        st.session_state.location_confirmed = False

    with st.form("incident_form", clear_on_submit=False):
        col1, col2 = st.columns(2)

        with col1:
            title = st.text_input(
                "Título del Incidente *", placeholder="Ej: Bache en calle principal"
            )
            category = st.selectbox("Categoría *", get_category_options())
            severity = st.selectbox("Severidad *", get_severity_options())

        with col2:
            reporter_name = st.text_input(
                "Nombre del Reportador *", placeholder="Su nombre completo"
            )
            reporter_contact = st.text_input(
                "Contacto *", placeholder="Teléfono o email"
            )

        description = st.text_area(
            "Descripción Detallada *",
            height=120,
            placeholder="Describa el incidente con el mayor detalle posible, incluyendo circunstancias, fecha aproximada, etc.",
        )

        st.markdown("---")
        st.subheader("📍 Ubicación del Incidente *")

        location_method = st.radio(
            "Método de ubicación:",
            [
                "🔍 Buscar dirección",
                "📍 Usar mi ubicación actual",
                "🗺️ Seleccionar en mapa",
            ],
            horizontal=True,
        )

        location_data = {}

        search_col1, search_col2 = st.columns([3, 1])

        if location_method == "🔍 Buscar dirección":
            with search_col1:
                address = st.text_input(
                    "Ingrese la dirección:",
                    placeholder="Ej: Calle 72 # 45-12, Bogotá",
                    key="address_input",
                )
            with search_col2:
                st.markdown("<br>", unsafe_allow_html=True)
                search_btn = st.form_submit_button(
                    "🔍 Buscar", use_container_width=True
                )

            if search_btn and address:
                with st.spinner(f"🔎 Buscando: {address}..."):
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
                        st.session_state.pending_location = location_data
                        st.session_state.location_confirmed = True
                        st.success(f"✅ Ubicación encontrada: {location.address}")
                        st.session_state.map_center = [
                            location.latitude,
                            location.longitude,
                        ]
                    else:
                        st.error(
                            "❌ No se pudo encontrar la ubicación. Intente con una dirección más específica."
                        )

        elif location_method == "📍 Usar mi ubicación actual":
            st.info("🌐 Obteniendo su ubicación basada en IP...")
            if st.form_submit_button("📍 Obtener mi ubicación"):
                with st.spinner("Obteniendo ubicación..."):
                    location = geo_service.get_ip_location()
                    if location:
                        location_data = {
                            "latitude": location.latitude,
                            "longitude": location.longitude,
                            "address": f"{location.city}, {location.country}",
                            "city": location.city,
                            "country": location.country,
                        }
                        st.session_state.pending_location = location_data
                        st.session_state.location_confirmed = True
                        st.success(
                            f"✅ Ubicación obtenida: {location.city}, {location.country}"
                        )
                        st.session_state.map_center = [
                            location.latitude,
                            location.longitude,
                        ]
                    else:
                        st.error("❌ No se pudo obtener la ubicación")

        elif location_method == "🗺️ Seleccionar en mapa":
            st.info("🗺️ Haga clic en el mapa para seleccionar la ubicación")

            m = folium.Map(
                location=st.session_state.get("map_center", DEFAULT_MAP_CENTER),
                zoom_start=12,
                tiles=get_geoapify_tiles(GEOAPIFY_API_KEY),
                attr='&copy; <a href="https://www.geoapify.com/">Geoapify</a>',
            )

            clicked = st_folium(
                m,
                width=700,
                height=400,
                key="selection_map",
                returned_objects=["last_clicked"],
            )

            col_lat, col_lon = st.columns(2)
            with col_lat:
                lat = st.number_input(
                    "Latitud", value=4.5709, step=0.0001, format="%.6f", key="lat_input"
                )
            with col_lon:
                lon = st.number_input(
                    "Longitud",
                    value=-74.2973,
                    step=0.0001,
                    format="%.6f",
                    key="lon_input",
                )

            if clicked.get("last_clicked"):
                lat = clicked["last_clicked"]["lat"]
                lon = clicked["last_clicked"]["lng"]
                st.session_state.map_center = [lat, lon]

            if st.form_submit_button("📍 Confirmar ubicación"):
                with st.spinner("Revirtiendo geocodificación..."):
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
                        st.session_state.pending_location = location_data
                        st.session_state.location_confirmed = True
                        st.success(f"✅ Ubicación confirmada: {location.address}")
                    else:
                        location_data = {
                            "latitude": lat,
                            "longitude": lon,
                            "address": f"Coordenadas: {lat}, {lon}",
                            "city": "Desconocida",
                            "country": "Desconocido",
                        }
                        st.session_state.pending_location = location_data
                        st.session_state.location_confirmed = True

        if st.session_state.location_confirmed and st.session_state.pending_location:
            loc = st.session_state.pending_location
            st.markdown(
                """
            <div style="background-color: #E8F5E9; padding: 15px; border-radius: 8px; border-left: 4px solid #4CAF50; margin: 15px 0;">
                <h4 style="margin: 0; color: #2E7D32;">📍 Ubicación Confirmada</h4>
                <p style="margin: 5px 0;"><strong>Dirección:</strong> {}</p>
                <p style="margin: 5px 0;"><strong>Ciudad:</strong> {} | <strong>País:</strong> {}</p>
                <p style="margin: 5px 0; font-size: 12px; color: #666;">🗺️ Coordenadas: ({:.6f}, {:.6f})</p>
            </div>
            """.format(
                    loc.get("address", "N/A"),
                    loc.get("city", "N/A"),
                    loc.get("country", "N/A"),
                    loc.get("latitude", 0),
                    loc.get("longitude", 0),
                ),
                unsafe_allow_html=True,
            )

        st.markdown("---")

        submitted = st.form_submit_button(
            "📨 Enviar Reporte", type="primary", use_container_width=True
        )

        if submitted:
            if (
                not title
                or not description
                or not reporter_name
                or not reporter_contact
            ):
                st.error("⚠️ Por favor complete todos los campos marcados con (*)")
            elif not st.session_state.location_confirmed:
                st.error("⚠️ Por favor seleccione una ubicación para el incidente")
            else:
                incident = Incident(
                    id="",
                    title=title,
                    description=description,
                    category=category,
                    severity=severity,
                    location=st.session_state.pending_location,
                    reporter_name=reporter_name,
                    reporter_contact=reporter_contact,
                    created_at="",
                )

                created = storage.create_incident(incident)

                st.session_state.pending_location = None
                st.session_state.location_confirmed = False

                st.success(f"✅ Incidente reportado exitosamente!")
                st.info(f"📋 ID del reporte: `{created.id}`")
                st.balloons()


def page_map():
    st.title("🗺️ Mapa de Incidentes")
    st.markdown(
        "Visualización geoespacial interactiva de todos los incidentes reportados"
    )

    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

    with col1:
        st.markdown("### 🗺️ Filtrar por:")

    with col2:
        filter_category = st.selectbox("Categoría", ["Todas"] + get_category_options())
    with col3:
        filter_severity = st.selectbox("Severidad", ["Todas"] + get_severity_options())
    with col4:
        filter_status = st.selectbox("Estado", ["Todos"] + get_status_options())

    incidents = storage.get_all_incidents()

    if filter_category != "Todas":
        incidents = [i for i in incidents if i.category == filter_category]
    if filter_severity != "Todas":
        incidents = [i for i in incidents if i.severity == filter_severity]
    if filter_status != "Todos":
        incidents = [i for i in incidents if i.status == filter_status]

    st.markdown(f"**Total de incidentes mostrados:** `{len(incidents)}`")

    if incidents:
        col_map, col_info = st.columns([3, 1])

        with col_map:
            map_obj = create_incident_map(
                incidents,
                center=st.session_state.get("map_center", DEFAULT_MAP_CENTER),
                api_key=GEOAPIFY_API_KEY,
            )
            st_folium(map_obj, width=1000, height=650, key="full_map")

        with col_info:
            st.markdown("### 📊 Leyenda")
            st.markdown("**Categorías:**")
            for cat, emoji in CATEGORY_EMOJI.items():
                st.markdown(f"{emoji} {cat.capitalize()}")

            st.markdown("---")
            st.markdown("**Severidad:**")
            for sev, color in SEVERITY_COLORS.items():
                st.markdown(
                    f"🟢 {sev.capitalize()}"
                    if color == "green"
                    else f"🟠 {sev.capitalize()}"
                    if color == "orange"
                    else f"🔴 {sev.capitalize()}"
                )
    else:
        m = folium.Map(
            location=DEFAULT_MAP_CENTER,
            zoom_start=10,
            tiles=get_geoapify_tiles(GEOAPIFY_API_KEY),
            attr='&copy; <a href="https://www.geoapify.com/">Geoapify</a>',
        )
        st_folium(m, width=1000, height=600)
        st.warning("⚠️ No hay incidentes que coincidan con los filtros seleccionados")


def page_list():
    st.title("📋 Lista de Incidentes")
    st.markdown("Explorar y gestionar todos los incidentes reportados")

    col1, col2, col3 = st.columns(3)

    with col1:
        filter_category = st.selectbox(
            "Filtrar por Categoría", ["Todas"] + get_category_options(), key="list_cat"
        )
    with col2:
        filter_severity = st.selectbox(
            "Filtrar por Severidad", ["Todas"] + get_severity_options(), key="list_sev"
        )
    with col3:
        filter_status = st.selectbox(
            "Filtrar por Estado", ["Todos"] + get_status_options(), key="list_stat"
        )

    incidents = storage.get_all_incidents()

    if filter_category != "Todas":
        incidents = [i for i in incidents if i.category == filter_category]
    if filter_severity != "Todas":
        incidents = [i for i in incidents if i.severity == filter_severity]
    if filter_status != "Todos":
        incidents = [i for i in incidents if i.status == filter_status]

    st.markdown(f"**Total de incidentes:** `{len(incidents)}`")

    if not incidents:
        st.info("No hay incidentes para mostrar")
        return

    for i, incident in enumerate(incidents):
        render_incident_card(incident)

        col1, col2, col3 = st.columns([2, 2, 1])

        with col1:
            new_status = st.selectbox(
                "Cambiar Estado",
                get_status_options(),
                index=get_status_options().index(incident.status)
                if incident.status in get_status_options()
                else 0,
                key=f"status_{incident.id}_{i}",
            )

        with col2:
            if new_status != incident.status:
                if st.button(f"✅ Actualizar estado", key=f"btn_{incident.id}_{i}"):
                    storage.update_incident(incident.id, {"status": new_status})
                    st.success("✅ Estado actualizado correctamente")
                    st.rerun()

        with col3:
            if st.button(f"🗑️ Eliminar", key=f"del_{incident.id}_{i}"):
                if storage.delete_incident(incident.id):
                    st.success("🗑️ Incidente eliminado")
                    st.rerun()

        st.markdown("---")


def page_statistics():
    st.title("📈 Estadísticas")
    st.markdown("Análisis detallado y métricas de los incidentes reportados")

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
            severity_color = SEVERITY_COLORS.get(incident.severity, "blue")
            category_emoji = CATEGORY_EMOJI.get(incident.category, "📌")
            st.markdown(f"""
            **{category_emoji} {incident.title}** - {incident.category} - 
            :{severity_color}[{incident.severity}] - 
            {datetime.fromisoformat(incident.created_at).strftime("%Y-%m-%d %H:%M")}*
            """)


def page_settings():
    st.title("⚙️ Configuración")
    st.markdown("Configuración del sistema y API")

    st.subheader("🗺️ API de Geoapify")

    col1, col2 = st.columns([2, 1])

    with col1:
        api_key_input = st.text_input(
            "API Key de Geoapify",
            value=GEOAPIFY_API_KEY,
            type="password",
            help="API key para usar los servicios de geocodificación y mapas de Geoapify",
        )

    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Probar conexión"):
            with st.spinner("Probando conexión con Geoapify..."):
                test_location = geo_service.geocode("Bogotá, Colombia")
                if test_location:
                    st.success(
                        f"✅ Conexión exitosa: {test_location.city}, {test_location.country}"
                    )
                else:
                    st.error("❌ Error de conexión. Verifique la API key.")

    st.markdown("---")
    st.subheader("📊 Información del Sistema")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Incidentes", storage.get_statistics().get("total", 0))
    with col2:
        st.metric("Categorías Disponibles", len(get_category_options()))
    with col3:
        st.metric("Niveles de Severidad", len(get_severity_options()))

    st.markdown("---")
    st.subheader("ℹ️ Acerca de")
    st.markdown("""
    **GeoReport Provider v1.0.0**
    
    Sistema de gestión y reporte de incidentes georreferenciados.
    
    ---
    
    **Tecnologías:**
    - 🗺️ **Mapas:** Geoapify API
    - 📱 **Frontend:** Streamlit
    - 💾 **Almacenamiento:** JSON (local)
    - 🌍 **Despliegue:** Streamlit Cloud
    
    ---
    
    **URL de API utilizada:**
    ```
    https://api.geoapify.com/v1/geocode/search
    ```
    
    © 2026 GeoReport - Todos los derechos reservados.
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
