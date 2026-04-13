import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.auth_db import init_db, verify_user, create_user


def init_auth_session():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user" not in st.session_state:
        st.session_state.user = None
    if "auth_initialized" not in st.session_state:
        init_db()
        st.session_state.auth_initialized = True


COLORS = {
    "primary": "#0D47A1",
    "primary_light": "#1565C0",
    "primary_dark": "#0A3065",
    "secondary": "#42A5F5",
    "accent": "#64B5F6",
    "background": "#F5F8FA",
    "card_bg": "#FFFFFF",
    "text": "#1A1A2E",
    "text_secondary": "#5A6A7A",
    "success": "#2E7D32",
    "error": "#C62828",
    "warning": "#F57C00",
}


def render_styles():
    st.markdown(
        f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {{
        font-family: 'Inter', sans-serif;
    }}
    
    .stApp {{
        background: linear-gradient(135deg, {COLORS["background"]} 0%, #E3F2FD 50%, {COLORS["background"]} 100%);
    }}
    
    .auth-container {{
        max-width: 480px;
        margin: 0 auto;
        padding: 40px 30px;
    }}
    
    .auth-card {{
        background: {COLORS["card_bg"]};
        border-radius: 20px;
        padding: 40px;
        box-shadow: 0 10px 40px rgba(13, 71, 161, 0.15);
        border: 1px solid rgba(13, 71, 161, 0.1);
    }}
    
    .logo-container {{
        text-align: center;
        margin-bottom: 30px;
    }}
    
    .logo-icon {{
        font-size: 72px;
        display: block;
        margin-bottom: 10px;
    }}
    
    .logo-title {{
        color: {COLORS["primary"]};
        font-size: 32px;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }}
    
    .logo-subtitle {{
        color: {COLORS["text_secondary"]};
        font-size: 14px;
        margin-top: 8px;
        font-weight: 400;
    }}
    
    .logo-description {{
        background: linear-gradient(135deg, {COLORS["primary"]} 0%, {COLORS["primary_light"]} 100%);
        color: white;
        padding: 15px 20px;
        border-radius: 12px;
        margin-top: 20px;
        font-size: 13px;
        line-height: 1.6;
    }}
    
    .form-header {{
        color: {COLORS["primary"]};
        font-size: 24px;
        font-weight: 600;
        margin-bottom: 8px;
        text-align: center;
    }}
    
    .form-subheader {{
        color: {COLORS["text_secondary"]};
        font-size: 14px;
        margin-bottom: 30px;
        text-align: center;
    }}
    
    .input-group {{
        margin-bottom: 20px;
    }}
    
    .input-label {{
        color: {COLORS["text"]};
        font-size: 13px;
        font-weight: 500;
        margin-bottom: 8px;
        display: block;
    }}
    
    .stTextInput > div > div > input {{
        background: {COLORS["background"]};
        border: 2px solid #E0E7FF;
        border-radius: 12px;
        padding: 14px 16px;
        font-size: 15px;
        transition: all 0.3s ease;
    }}
    
    .stTextInput > div > div > input:focus {{
        border-color: {COLORS["primary"]};
        box-shadow: 0 0 0 4px rgba(13, 71, 161, 0.1);
        outline: none;
    }}
    
    .stPassword > div > div > input {{
        background: {COLORS["background"]};
        border: 2px solid #E0E7FF;
        border-radius: 12px;
        padding: 14px 16px;
        font-size: 15px;
    }}
    
    .stPassword > div > div > input:focus {{
        border-color: {COLORS["primary"]};
        box-shadow: 0 0 0 4px rgba(13, 71, 161, 0.1);
        outline: none;
    }}
    
    .submit-btn button {{
        background: linear-gradient(135deg, {COLORS["primary"]} 0%, {COLORS["primary_light"]} 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 16px 24px;
        font-size: 16px;
        font-weight: 600;
        width: 100%;
        transition: all 0.3s ease;
        margin-top: 10px;
    }}
    
    .submit-btn button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(13, 71, 161, 0.3);
    }}
    
    .divider {{
        display: flex;
        align-items: center;
        margin: 25px 0;
    }}
    
    .divider-line {{
        flex: 1;
        height: 1px;
        background: #E0E7FF;
    }}
    
    .divider-text {{
        padding: 0 15px;
        color: {COLORS["text_secondary"]};
        font-size: 13px;
    }}
    
    .register-link {{
        text-align: center;
        color: {COLORS["text_secondary"]};
        font-size: 14px;
    }}
    
    .register-link a {{
        color: {COLORS["primary"]};
        font-weight: 600;
        text-decoration: none;
    }}
    
    .register-link a:hover {{
        text-decoration: underline;
    }}
    
    .features-grid {{
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 12px;
        margin-top: 20px;
    }}
    
    .feature-item {{
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 12px;
        color: {COLORS["text_secondary"]};
    }}
    
    .feature-icon {{
        font-size: 16px;
    }}
    
    .info-box {{
        background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
        border-radius: 12px;
        padding: 20px;
        margin-top: 25px;
        border-left: 4px solid {COLORS["primary"]};
    }}
    
    .info-box-title {{
        color: {COLORS["primary"]};
        font-weight: 600;
        font-size: 14px;
        margin-bottom: 8px;
    }}
    
    .info-box-text {{
        color: {COLORS["text_secondary"]};
        font-size: 13px;
        line-height: 1.5;
    }}
    
    .back-link {{
        text-align: center;
        margin-top: 20px;
    }}
    
    .back-link a {{
        color: {COLORS["text_secondary"]};
        text-decoration: none;
        font-size: 14px;
    }}
    
    .back-link a:hover {{
        color: {COLORS["primary"]};
    }}
    
    .stAlert {{
        border-radius: 12px;
    }}
    </style>
    """,
        unsafe_allow_html=True,
    )


def page_login():
    st.set_page_config(
        page_title="SAFE - Seguridad Inteligente",
        page_icon="🛡️",
        layout="centered",
    )

    init_auth_session()
    render_styles()

    st.markdown('<div class="auth-container">', unsafe_allow_html=True)

    st.markdown(
        f"""
    <div class="auth-card">
        <div class="logo-container">
            <span class="logo-icon">🛡️</span>
            <h1 class="logo-title">SAFE</h1>
            <p class="logo-subtitle">Seguridad Inteligente y Siempre Activa</p>
            <div class="logo-description">
                <strong>🔮 Motor de Predicción de Eventos de Seguridad</strong><br>
                Sistema predictivo con IA que anticipa incidentes, analiza patrones geográficos 
                y temporales para proteger a tu comunidad. Reporta, predice y previene.
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="form-header">¡Bienvenido de nuevo!</div>', unsafe_allow_html=True
    )
    st.markdown(
        '<div class="form-subheader">Inicia sesión para continuar</div>',
        unsafe_allow_html=True,
    )

    with st.form("login_form"):
        col1, col2 = st.columns([1, 1])
        with col1:
            username = st.text_input(
                "Usuario", placeholder="Tu usuario", label_visibility="collapsed"
            )
        with col2:
            password = st.text_input(
                "Contraseña",
                type="password",
                placeholder="Tu contraseña",
                label_visibility="collapsed",
            )

        col_submit, _ = st.columns([1, 1])
        with col_submit:
            submitted = st.form_submit_button(
                "🔐 Iniciar Sesión", use_container_width=True
            )

        if submitted:
            if not username or not password:
                st.error("⚠️ Por favor completa todos los campos")
            else:
                user = verify_user(username, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos")

    st.markdown(
        f"""
        <div class="divider">
            <div class="divider-line"></div>
            <div class="divider-text">¿No tienes cuenta?</div>
            <div class="divider-line"></div>
        </div>
        
        <div class="register-link">
            <a href="?page=register" onclick="document.getElementById('register-btn').click()">
                📝 Crear cuenta en SAFE
            </a>
        </div>
    """,
        unsafe_allow_html=True,
    )

    if st.button(
        "📝 Crear cuenta en SAFE", key="register_btn", use_container_width=True
    ):
        st.switch_page("?page=register")

    st.markdown("</div></div>", unsafe_allow_html=True)


def page_register():
    st.set_page_config(
        page_title="SAFE - Registro",
        page_icon="🛡️",
        layout="centered",
    )

    init_auth_session()
    render_styles()

    st.markdown('<div class="auth-container">', unsafe_allow_html=True)

    st.markdown(
        f"""
    <div class="auth-card">
        <div class="logo-container">
            <span class="logo-icon">🛡️</span>
            <h1 class="logo-title">SAFE</h1>
            <p class="logo-subtitle">Seguridad Inteligente y Siempre Activa</p>
        </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="form-header">Crear Cuenta</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="form-subheader">Únete a la comunidad SAFE</div>',
        unsafe_allow_html=True,
    )

    with st.form("register_form"):
        full_name = st.text_input("Nombre Completo", placeholder="Tu nombre completo")

        col1, col2 = st.columns(2)
        with col1:
            username = st.text_input("Usuario *", placeholder="Nombre de usuario")
        with col2:
            email = st.text_input("Correo Electrónico *", placeholder="tu@email.com")

        phone = st.text_input("Teléfono", placeholder="+57 300 123 4567")

        col3, col4 = st.columns(2)
        with col3:
            password = st.text_input(
                "Contraseña *", type="password", placeholder="Mín. 6 caracteres"
            )
        with col4:
            confirm_password = st.text_input(
                "Confirmar *", type="password", placeholder="Confirmar contraseña"
            )

        submitted = st.form_submit_button(
            "✅ Crear Mi Cuenta SAFE", use_container_width=True
        )

        if submitted:
            if not username or not email or not password:
                st.error("⚠️ Los campos con * son obligatorios")
            elif password != confirm_password:
                st.error("⚠️ Las contraseñas no coinciden")
            elif len(password) < 6:
                st.error("⚠️ La contraseña debe tener al menos 6 caracteres")
            else:
                try:
                    user = create_user(username, email, password, full_name, phone)
                    st.success("✅ ¡Cuenta creada exitosamente!")
                    st.info("Ahora puedes iniciar sesión")

                    st.markdown("---")
                    if st.button("🔐 Ir a Login", use_container_width=True):
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {e}")

    st.markdown(
        """
        <div class="back-link">
            <a href="?page=login">← Volver al login</a>
        </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("</div></div>", unsafe_allow_html=True)


def render_auth_sidebar():
    if st.session_state.get("logged_in") and st.session_state.get("user"):
        user = st.session_state.user
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 👤 Usuario")
        st.sidebar.markdown(f"**{user.get('username', '')}**")
        st.sidebar.markdown(f"_{user.get('email', '')}_")

        if user.get("phone"):
            st.sidebar.markdown(f"📱 {user.get('phone')}")

        if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.rerun()


def require_auth():
    if not st.session_state.get("logged_in"):
        st.warning("🔒 Por favor, inicie sesión para acceder")
        st.page_link("?page=login", label="🔐 Ir a Login")
        st.stop()
