# 🛡️ SAFE GeoReport

Sistema de Gestión de Incidentes Georreferenciados basado en la **SEGMENTACIÓN ESTRATÉGICA DE LAS VARIABLES DE REPORTE**.

---

## Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                      SAFE GEOREPORT                              │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │   Frontend  │  │   Backend   │  │   Storage   │          │
│  │  (Streamlit)│◄─►│  (Python)   │◄─►│   (JSON)    │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
│         │                 │                 │                     │
│         └─────────────────┼─────────────────┘                     │
│                           ▼                                       │
│              ┌─────────────────────────┐                         │
│              │    Geoapify API         │                         │
│              │  (Geocodificación)     │                         │
│              └─────────────────────────┘                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## Segmentación Estratégica de Variables

El sistema implementa la **SEGMENTACIÓN ESTRATÉGICA DE LAS VARIABLES DE REPORTE** con tres niveles de categorización:

---

### 🎯 1. Panel de Acceso Directo (Variables de Mayor Interés Territorial)

*6 categorías de alta frecuencia de ocurrencia e impacto directo en la percepción de seguridad ciudadana.*

| ID | Nombre | Icono | Descripción |
|----|--------|-------|-------------|
| hurto_personas | Hurto a Personas | 🎯 | Reportes rápidos de robos sin violencia extrema |
| hurto_comercios | Hurto a Comercios | 🏪 | Incidentes de robo en establecimientos locales |
| hurto_vehiculos | Hurto a Vehículos | 🚗 | Incluye partes de vehículos y motocicletas |
| hurto_residencias | Hurto a Residencias | 🏠 | Violación de la propiedad privada |
| violencia_intrafamiliar | Violencia Intrafamiliar | ⚠️ | Reportes de agresiones dentro del núcleo hogar |
| extorsion | Extorsión | 💰 | Cobros indebidos o vacunas en sectores comerciales |

---

### ⚖️ 2. Incidentes de Convivencia (Ley 1801/2016)

*Listado detallado para reportes comunitarios. Diseñado para reportes comunitarios con opción de anonimato.*

| ID | Nombre | Icono | Descripción |
|----|--------|-------|-------------|
| alteraciones_orden | Alteraciones al Orden Público | 📢 | Reportes de comportamiento disruptivo en espacios públicos |
| extorsion_menor | Extorsión Menor | 💵 | Cobros indebidos o vacunas en sectores comerciales |
| lesiones_personales | Lesiones Personales | 🩹 | Conflictos físicos menores |
| rinas_callejeras | Riñas Callejeras | 👊 | Peleas en vía pública |
| ruido_excesivo | Ruido Excesivo | 🔊 | Contaminación auditiva que afecta la paz vecinal |
| vandalismo | Vandalismo | 🔨 | Daños a bienes públicos o privados |
| otro_convivencia | Otro (¿Cuál?) | 📝 | Campo de texto abierto para casos no tipificados |

---

### ⚖️ 3. Delitos de Bajo y Mediano Impacto (Ley 599/2000)

*Para el flujo formal de denuncias, el lenguaje se ajusta a términos legales para facilitar la vinculación con la Fiscalía y la Policía.*

| ID | Nombre | Icono | Descripción |
|----|--------|-------|-------------|
| delitos_sexuales | Delitos Sexuales Menores | 🚫 | Casos que requieren manejo de evidencia confidencial |
| extorsion_delito | Extorsión | 💰 | Denuncia formal para investigación institucional |
| lesiones_personales_delito | Lesiones Personales | 🩹 | Agresiones físicas documentadas para procesos legales |
| violencia_genero | Violencia de Género | ⚧️ | Denuncias específicas protegidas por protocolos de seguridad |
| otro_delito | Otro (¿Cuál?) | 📝 | Selección para delitos que no figuren en el menú principal |

---

### ⚠️ Niveles de Severidad

| Nivel | Color | Descripción |
|-------|-------|-------------|
| Crítico | ⛔ | Riesgo inmediato a vidas o propiedad |
| Alto | 🔴 | Impacto significativo requiere atención urgente |
| Medio | 🟠 | Impacto moderado requiere atención |
| Bajo | 🟢 | Impacto mínimo o cosmético |

---

### 📊 Estados del Reporte

1. 📥 Recibido
2. 🔍 Validando
3. 👤 Asignado
4. ⚙️ En Proceso
5. ✅ Resuelto
6. 🔒 Cerrado
7. ❌ Rechazado

---

### 📢 Fuentes de Reporte

- 👤 Ciudadano
- 📹 Cámaras de Seguridad
- 📡 Sensores IoT
- 📞 Línea de Emergencias
- 🌐 Portal Web
- 📱 App Móvil
- 📢 Redes Sociales

---

## Funcionalidades

### 🏠 Dashboard
- Vista general del sistema
- Métricas principales (total, activos)
- Mapa de todos los incidentes centrado en Medellín
- Panel lateral con conteos por categoría

### 📝 Nuevo Reporte

Formulario guiado con segmentación estratégica:

1. **Panel de Acceso Directo** - Muestra las 6 categorías principales
2. **Tipo de Reporte** - Seleccionar entre:
   - 🎯 Panel de Acceso Directo (6 categorías)
   - ⚖️ Incidentes de Convivencia (Ley 1801/2016)
   - ⚖️ Delitos (Ley 599/2000)
3. **Categoría** - Cambia dinámicamente según el tipo de reporte
4. **Ubicación del Incidente**:
   - Campo de búsqueda de dirección
   - Coordenadas editables (Latitud/Longitud)
   - Mapa interactivo para seleccionar ubicación
   - **Botón "Confirmar Ubicación"** para validar
5. **Datos del Reporte**:
   - Título, Reportante (opción anónima), Contacto
   - Severidad, Fuente
   - Descripción detallada
6. **Envío** con timestamp automático y georreferenciación

### 🗺️ Mapa Global

- Visualización de todos los incidentes georreferenciados
- Estadísticas del mapa (Total, Con Ubicación, Activos)
- Filtros por categoría y severidad
- Marcadores interactivos con popups
- Centrado en Medellín
- Colores por severidad

### 📋 Todos los Reportes

- Lista completa de incidentes
- Filtros por categoría
- Detalle de cada incidente (ubicación, coordenadas)
- Cambio de estado
- Eliminación de reportes

### 📈 Analytics

- Estadísticas detalladas
- Gráficos por categoría
- Distribución por severidad

### ⚙️ Configuración

- Información del sistema
- Prueba de conexión API
- Detalles de segmentación estratégica

---

## Flujo de Registro de Incidentes

```
┌──────────────────────────────────────────────────────────────┐
│                    REGISTRO DE INCIDENTE                     │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Seleccionar Tipo de Reporte                             │
│     └─► Panel de Acceso Directo / Convivencia / Delito       │
│                                                              │
│  2. Seleccionar Categoría (dinámico según tipo)             │
│                                                              │
│  3. Ubicación del Incidente                                 │
│     ├─► Buscar dirección (Geoapify)                         │
│     ├─► Editar coordenadas manualmente                       │
│     ├─► Seleccionar en mapa interactivo                     │
│     └─► ✅ Confirmar Ubicación                             │
│                                                              │
│  4. Datos del Reporte                                       │
│     ├─► Título, Reportante, Contacto                        │
│     ├─► Severidad, Fuente                                  │
│     └─► Descripción detallada                              │
│                                                              │
│  5. Enviar Reporte                                          │
│     └─► Timestamp automático + Georreferenciación           │
│                                                              │
│  6. Verificación                                            │
│     ├─► Mapa con ubicación exacta del incidente             │
│     └─► Botón para ver en Mapa Global                      │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## Estructura de Archivos

```
georeferencia/
├── app.py                 # Aplicación principal
├── requirements.txt       # Dependencias Python
├── README.md              # Este archivo
├── data/
│   └── incidents.json    # Base de datos de incidentes
├── .streamlit/
│   ├── config.toml       # Configuración de Streamlit
│   └── secrets.toml     # Secrets (API keys)
├── .env.example          # Variables de entorno ejemplo
├── Geo APIKEY.txt        # Archivo de API (referencia)
└── SEGMENTACIÓN ESTRATÉGICA DE LAS VARIABLES DE REPORTE.docx
```

---

## Uso del Sistema

### Ejecución Local

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Ejecutar la aplicación
streamlit run app.py
```

La aplicación estará disponible en: `http://localhost:8501`

---

## Nota de Implementación

> Cada reporte **dispara automáticamente**:
> - **Timestamp:** Fecha y hora exactas del reporte
> - **Georreferenciación:** Coordenadas exactas del incidente
> - **Confirmación de Ubicación:** Validación antes de registrar
>
> Esto asegura que la data sea **"Verificable para IA"** y útil para el análisis de patrones delictivos en tiempo real.

---

## Características Técnicas

- **Framework UI:** Streamlit
- **Mapas:** Folium + Geoapify
- **Storage:** JSON local
- **API:** Geoapify RESTful (Geocodificación y Búsqueda)
- **Responsive:** Sí
- **Localización:** Medellín, Colombia

---

## Licencia

© 2026 SAFE Inteligencia Segura - Todos los derechos reservados.
