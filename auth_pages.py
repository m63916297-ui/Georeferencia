"""
🛡️ SAFE - Páginas de Autenticación
=============================

Páginas de login y registro para SAFE - Motor de Predicción de Eventos
Diseño basado en paleta de colores SAFE: Azul #0D47A1, Cyan #42A5F5, Blanco

Autor: SAFE Inteligencia Segura
Versión: 1.0.0
"""

import streamlit as st
from datetime import datetime
from typing import Optional, Dict, List
import os
import json
import uuid
import hashlib

USERS_FILE = "data/users.json"


class AuthDB:
    """Sistema de gestión de usuarios"""

    def __init__(self, file_path: str = USERS_FILE):
        self.file_path = file_path
        self._ensure_file()

    def _ensure_file(self):
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            self._write([])

    def _read(self) -> List[Dict]:
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _write(self, data: List[Dict]):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        nombre: str = "",
        rol: str = "usuario",
    ) -> Optional[Dict]:
        users = self._read()

        for u in users:
            if u.get("username") == username:
                return None
            if u.get("email") == email:
                return None

        user = {
            "id": str(uuid.uuid4()),
            "username": username,
            "email": email,
            "password": self._hash_password(password),
            "nombre": nombre or username,
            "rol": rol,
            "created_at": datetime.now().isoformat(),
            "last_login": None,
            "activo": True,
        }

        users.append(user)
        self._write(users)
        return user

    def authenticate(self, username: str, password: str) -> Optional[Dict]:
        users = self._read()
        hashed = self._hash_password(password)

        for u in users:
            if (u.get("username") == username or u.get("email") == username) and u.get(
                "password"
            ) == hashed:
                if u.get("activo", True):
                    u["last_login"] = datetime.now().isoformat()
                    self._write(users)
                    return u
        return None

    def get_user(self, username: str) -> Optional[Dict]:
        users = self._read()
        for u in users:
            if u.get("username") == username or u.get("email") == username:
                return u
        return None

    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        users = self._read()
        for u in users:
            if u.get("id") == user_id:
                return u
        return None

    def update_user(self, user_id: str, updates: Dict) -> Optional[Dict]:
        users = self._read()
        for i, u in enumerate(users):
            if u.get("id") == user_id:
                u.update(updates)
                u["updated_at"] = datetime.now().isoformat()
                users[i] = u
                self._write(users)
                return u
        return None


auth_db = AuthDB()


def init_auth_session():
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "username" not in st.session_state:
        st.session_state.username = None
    if "user_email" not in st.session_state:
        st.session_state.user_email = None
    if "user_nombre" not in st.session_state:
        st.session_state.user_nombre = None
    if "user_rol" not in st.session_state:
        st.session_state.user_rol = None
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "mostrar_registro" not in st.session_state:
        st.session_state.mostrar_registro = False


def login_user(user: Dict):
    st.session_state.user_id = user.get("id")
    st.session_state.username = user.get("username")
    st.session_state.user_email = user.get("email")
    st.session_state.user_nombre = user.get("nombre")
    st.session_state.user_rol = user.get("rol")
    st.session_state.logged_in = True


def logout_user():
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.user_email = None
    st.session_state.user_nombre = None
    st.session_state.user_rol = None
    st.session_state.logged_in = False


def require_auth():
    if not st.session_state.get("logged_in"):
        st.warning("⚠️ Debes iniciar sesión para acceder a esta página")
        page_login()
        st.stop()


def render_auth_sidebar():
    if st.session_state.get("logged_in"):
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 👤 Usuario")

        nombre = st.session_state.get("user_nombre", "Usuario")
        username = st.session_state.get("username", "")
        rol = st.session_state.get("user_rol", "usuario")

        st.sidebar.markdown(f"**{nombre}**")
        st.sidebar.markdown(f"_{username}_")
        st.sidebar.markdown(f"📋 Rol: **{rol}**")

        if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True):
            logout_user()
            st.rerun()


def page_login():
    st.set_page_config(
        page_title="SAFE - Iniciar Sesión",
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    st.markdown(
        """
    <style>
    /* Paleta SAFE: Azul #0D47A1, Cyan #42A5F5, Blanco */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #0D47A1 0%, #1565C0 40%, #1976D2 60%, #42A5F5 100%) !important;
        font-family: 'Inter', sans-serif;
    }
    
    /* Login Container */
    .login-wrapper {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
        padding: 20px;
    }
    
    .login-card {
        background: rgba(255, 255, 255, 0.98);
        border-radius: 24px;
        padding: 48px;
        width: 100%;
        max-width: 420px;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.4);
    }
    
    /* Logo y Título */
    .login-header {
        text-align: center;
        margin-bottom: 36px;
    }
    
    .login-logo {
        width: 80px;
        height: 80px;
        background: linear-gradient(135deg, #0D47A1 0%, #42A5F5 100%);
        border-radius: 20px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 20px;
        box-shadow: 0 8px 20px rgba(13, 71, 161, 0.4);
    }
    
    .login-logo h1 {
        color: white;
        font-size: 36px;
        font-weight: 700;
        margin: 0;
    }
    
    .login-title {
        color: #0D47A1;
        font-size: 28px;
        font-weight: 700;
        margin: 0 0 8px 0;
    }
    
    .login-subtitle {
        color: #64748B;
        font-size: 15px;
        font-weight: 400;
        margin: 0;
    }
    
    /* Formularios */
    .login-form .stTextInput > div > div {
        border-radius: 12px;
        border: 2px solid #E2E8F0;
        background: #F8FAFC;
        padding: 4px 16px;
        transition: all 0.2s;
    }
    
    .login-form .stTextInput > div > div:focus-within {
        border-color: #42A5F5;
        background: white;
        box-shadow: 0 0 0 4px rgba(66, 165, 245, 0.15);
    }
    
    /* Labels */
    .login-form label {
        color: #334155;
        font-size: 14px;
        font-weight: 500 !important;
        margin-bottom: 6px;
        display: block;
    }
    
    /* Botón Primario */
    .btn-primary {
        background: linear-gradient(135deg, #0D47A1 0%, #1565C0 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 14px 24px !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        transition: all 0.2s !important;
        box-shadow: 0 4px 14px rgba(13, 71, 161, 0.4) !important;
    }
    
    .btn-primary:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(13, 71, 161, 0.5) !important;
    }
    
    /* Botón Secundario */
    .btn-secondary {
        background: transparent !important;
        color: #0D47A1 !important;
        border: 2px solid #0D47A1 !important;
        border-radius: 12px !important;
        padding: 14px 24px !important;
        font-weight: 600 !important;
        font-size: 15px !important;
    }
    
    .btn-secondary:hover {
        background: rgba(13, 71, 161, 0.05) !important;
    }
    
    /* Links */
    .login-link {
        color: #42A5F5;
        font-weight: 500;
        text-decoration: none;
    }
    
    .login-link:hover {
        color: #0D47A1;
        text-decoration: underline;
    }
    
    /* Footer */
    .login-footer {
        text-align: center;
        margin-top: 32px;
        padding-top: 24px;
        border-top: 1px solid #E2E8F0;
    }
    
    .login-footer p {
        color: #94A3B8;
        font-size: 13px;
        margin: 0;
    }
    
    /* Divider */
    .login-divider {
        display: flex;
        align-items: center;
        margin: 24px 0;
    }
    
    .login-divider::before,
    .login-divider::after {
        content: '';
        flex: 1;
        height: 1px;
        background: #E2E8F0;
    }
    
    .login-divider span {
        padding: 0 16px;
        color: #94A3B8;
        font-size: 13px;
    }
    
    /* Animación */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .login-card {
        animation: fadeIn 0.5s ease-out;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)

    with st.container():
        st.markdown(
            """
        <div class="login-card">
            <div class="login-header">
                <div class="login-logo">
                    <h1>🛡️</h1>
                </div>
                <h2 class="login-title">SAFE</h2>
                <p class="login-subtitle">Motor de Predicción de Eventos</p>
            </div>
        """,
            unsafe_allow_html=True,
        )

        with st.form("login_form", clear_on_submit=True):
            st.markdown('<div class="login-form">', unsafe_allow_html=True)

            username = st.text_input(
                "Usuario o Email",
                placeholder="Ingrese su usuario o correo electrónico",
            )
            password = st.text_input(
                "Contraseña",
                type="password",
                placeholder="Ingrese su contraseña",
            )

            col1, col2 = st.columns([1, 1])
            with col1:
                submit = st.form_submit_button(
                    "🔐 Iniciar Sesión",
                    use_container_width=True,
                )
            with col2:
                registro_btn = st.form_submit_button(
                    "📝 Crear Cuenta",
                    use_container_width=True,
                )

            if submit:
                if not username or not password:
                    st.error("⚠️ Por favor complete todos los campos")
                else:
                    user = auth_db.authenticate(username, password)
                    if user:
                        login_user(user)
                        st.success("✅ Iniciando sesión...")
                        st.rerun()
                    else:
                        st.error("❌ Usuario o contraseña incorrectos")

            if registro_btn:
                st.session_state.mostrar_registro = True
                st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(
            """
            <div class="login-footer">
                <p>🛡️ SAFE - Motor de Predicción de Eventos</p>
                <p style="margin-top: 4px;">© 2026 SAFE Inteligencia Segura</p>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)


def page_registro():
    st.set_page_config(
        page_title="SAFE - Registrarse",
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    st.markdown(
        """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #0D47A1 0%, #1565C0 40%, #1976D2 60%, #42A5F5 100%) !important;
        font-family: 'Inter', sans-serif;
    }
    
    .registro-wrapper {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
        padding: 20px;
    }
    
    .registro-card {
        background: rgba(255, 255, 255, 0.98);
        border-radius: 24px;
        padding: 40px;
        width: 100%;
        max-width: 480px;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.4);
    }
    
    .registro-header {
        text-align: center;
        margin-bottom: 32px;
    }
    
    .registro-logo {
        width: 72px;
        height: 72px;
        background: linear-gradient(135deg, #0D47A1 0%, #42A5F5 100%);
        border-radius: 18px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 16px;
        box-shadow: 0 8px 20px rgba(13, 71, 161, 0.4);
    }
    
    .registro-logo h1 {
        color: white;
        font-size: 32px;
        font-weight: 700;
        margin: 0;
    }
    
    .registro-title {
        color: #0D47A1;
        font-size: 26px;
        font-weight: 700;
        margin: 0 0 6px 0;
    }
    
    .registro-subtitle {
        color: #64748B;
        font-size: 14px;
        font-weight: 400;
        margin: 0;
    }
    
    /* Campos del formulario */
    .registro-form label {
        color: #334155;
        font-size: 14px;
        font-weight: 500 !important;
        margin-bottom: 6px;
        display: block;
    }
    
    .registro-form .stTextInput > div > div {
        border-radius: 12px;
        border: 2px solid #E2E8F0;
        background: #F8FAFC;
        padding: 4px 16px;
        transition: all 0.2s;
    }
    
    .registro-form .stTextInput > div > div:focus-within {
        border-color: #42A5F5;
        background: white;
        box-shadow: 0 0 0 4px rgba(66, 165, 245, 0.15);
    }
    
    /* Información adicional */
    .registro-info {
        background: #F0F9FF;
        border-left: 4px solid #42A5F5;
        padding: 16px;
        border-radius: 0 12px 12px 0;
        margin: 20px 0;
    }
    
    .registro-info p {
        color: #475569;
        font-size: 13px;
        margin: 0;
        line-height: 1.6;
    }
    
    .registro-footer {
        text-align: center;
        margin-top: 24px;
    }
    
    .registro-footer a {
        color: #42A5F5;
        font-weight: 500;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .registro-card {
        animation: fadeIn 0.5s ease-out;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="registro-wrapper">', unsafe_allow_html=True)

    with st.container():
        st.markdown(
            """
        <div class="registro-card">
            <div class="registro-header">
                <div class="registro-logo">
                    <h1>🛡️</h1>
                </div>
                <h2 class="registro-title">Crear Cuenta</h2>
                <p class="registro-subtitle">Únete a SAFE - Motor de Predicción de Eventos</p>
            </div>
        """,
            unsafe_allow_html=True,
        )

        with st.form("registro_form", clear_on_submit=True):
            st.markdown('<div class="registro-form">', unsafe_allow_html=True)

            username = st.text_input(
                "Usuario *",
                placeholder="Elige un nombre de usuario único",
            )
            email = st.text_input(
                "Email *",
                placeholder="tu@correo.com",
            )
            nombre = st.text_input(
                "Nombre Completo",
                placeholder="Tu nombre (opcional)",
            )
            password = st.text_input(
                "Contraseña *",
                type="password",
                placeholder="Mínimo 6 caracteres",
            )
            password_confirm = st.text_input(
                "Confirmar Contraseña *",
                type="password",
                placeholder="Repite la contraseña",
            )

            st.markdown(
                """
            <div class="registro-info">
                <p>🔒 <strong>Seguridad:</strong> Tu contraseña será encriptada de forma segura. 
                Los datos proporcionados se manejarán según nuestra política de privacidad.</p>
            </div>
            """,
                unsafe_allow_html=True,
            )

            col1, col2 = st.columns([1, 1])
            with col1:
                submit = st.form_submit_button(
                    "✓ Crear Cuenta",
                    use_container_width=True,
                )
            with col2:
                login_btn = st.form_submit_button(
                    "← Ya tengo cuenta",
                    use_container_width=True,
                )

            if submit:
                if not username or not email or not password:
                    st.error("⚠️ Complete los campos requeridos")
                elif len(password) < 6:
                    st.error("⚠️ La contraseña debe tener al menos 6 caracteres")
                elif password != password_confirm:
                    st.error("⚠️ Las contraseñas no coinciden")
                else:
                    user = auth_db.create_user(
                        username=username,
                        email=email,
                        password=password,
                        nombre=nombre,
                    )
                    if user:
                        st.success("✅ ¡Cuenta creada! Ahora puede iniciar sesión")
                        st.session_state.mostrar_registro = False
                        st.rerun()
                    else:
                        st.error("❌ El usuario o email ya están registrados")

            if login_btn:
                st.session_state.mostrar_registro = False
                st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(
            """
            <div class="registro-footer">
                <a href="#" onclick="_=null">¿Ya tienes cuenta? Inicia sesión</a>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)


def page_perfil():
    st.title("👤 Mi Perfil")

    if not st.session_state.get("logged_in"):
        st.warning("⚠️ Debes iniciar sesión")
        page_login()
        st.stop()

    user_id = st.session_state.get("user_id")
    user = auth_db.get_user_by_id(user_id)

    if user:
        st.markdown("### Información del Usuario")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Usuario:** {user.get('username')}")
            st.markdown(f"**Email:** {user.get('email')}")
        with col2:
            st.markdown(f"**Nombre:** {user.get('nombre')}")
            st.markdown(f"**Rol:** {user.get('rol')}")

        st.markdown("---")
        st.markdown(f"**Miembro desde:** {user.get('created_at', '')[:10]}")
        st.markdown(f"**Último acceso:** {user.get('last_login', 'Nunca')[:16]}")
