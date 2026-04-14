"""
🛡️ SAFE - Páginas de Autenticación Minimalista
=================================================

Diseño minimalista para SAFE - Motor de Predicción de Eventos
Basado en: Azul #0D47A1, Cyan #42A5F5

Autor: SAFE Inteligencia Segura
Versión: 2.0.0
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

    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        users = self._read()
        for u in users:
            if u.get("id") == user_id:
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


def render_auth_sidebar():
    if st.session_state.get("logged_in"):
        nombre = st.session_state.get("user_nombre", "Usuario")
        st.sidebar.markdown("---")
        with st.sidebar.container():
            st.sidebar.markdown(f"**{nombre}**")
            st.sidebar.markdown(f"_{st.session_state.get('username', '')}_")
            if st.sidebar.button("Cerrar Sesión", use_container_width=True):
                logout_user()
                st.rerun()


def inject_styles():
    st.markdown(
        """
    <style>
    /* Reset y base */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }
    
    /* Fondo minimalista */
    .stApp {
        background: linear-gradient(180deg, #0D47A1 0%, #1565C0 50%, #1E88E5 100%) !important;
    }
    
    /* Contenedor principal */
    .auth-container {
        max-width: 380px;
        margin: 0 auto;
        padding: 48px 32px;
        background: white;
        border-radius: 16px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.12);
    }
    
    /* Logo */
    .auth-logo {
        text-align: center;
        margin-bottom: 32px;
    }
    .auth-logo .shield {
        width: 56px;
        height: 56px;
        background: linear-gradient(135deg, #0D47A1, #42A5F5);
        border-radius: 14px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 28px;
        margin-bottom: 16px;
    }
    .auth-logo h2 {
        color: #0D47A1;
        font-size: 24px;
        font-weight: 600;
        margin: 0 0 4px 0;
    }
    .auth-logo p {
        color: #64748B;
        font-size: 14px;
        margin: 0;
    }
    
    /* Inputs minimalistas */
    .auth-container .stTextInput > div > div {
        border-radius: 8px;
        border: 1.5px solid #E2E8F0;
        background: #F8FAFC;
    }
    .auth-container .stTextInput > div > div:focus-within {
        border-color: #42A5F5;
        background: white;
        box-shadow: 0 0 0 3px rgba(66,165,245,0.1);
    }
    .auth-container .stTextInput label {
        font-size: 13px;
        font-weight: 500;
        color: #475569;
    }
    
    /* Botón primario */
    .auth-container .stButton > button[kind="primary"] {
        background: #0D47A1 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px !important;
        font-weight: 500 !important;
        width: 100%;
    }
    
    /* Botón secundario */
    .auth-container .stButton > button:not([kind="primary"]) {
        background: transparent !important;
        border: 1.5px solid #E2E8F0 !important;
        border-radius: 8px !important;
        padding: 12px !important;
        color: #475569 !important;
        width: 100%;
    }
    .auth-container .stButton > button:not([kind="primary"]):hover {
        border-color: #0D47A1 !important;
        color: #0D47A1 !important;
    }
    
    /* Footer */
    .auth-footer {
        text-align: center;
        margin-top: 24px;
        color: #94A3B8;
        font-size: 12px;
    }
    .auth-footer a {
        color: #42A5F5;
        text-decoration: none;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )


def page_login():
    inject_styles()

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container():
            st.markdown('<div class="auth-container">', unsafe_allow_html=True)

            st.markdown(
                """
            <div class="auth-logo">
                <div class="shield">🛡️</div>
                <h2>SAFE</h2>
                <p>Motor de Predicción de Eventos</p>
            </div>
            """,
                unsafe_allow_html=True,
            )

            with st.form("login_form", clear_on_submit=True):
                username = st.text_input(
                    "Usuario o Email", placeholder="Ingrese su usuario o email"
                )
                password = st.text_input(
                    "Contraseña", type="password", placeholder="••••••••"
                )

                c1, c2 = st.columns(2)
                with c1:
                    submit = st.form_submit_button(
                        "Iniciar Sesión", use_container_width=True
                    )
                with c2:
                    reg_btn = st.form_submit_button(
                        "Crear Cuenta", use_container_width=True
                    )

                if submit:
                    if not username or not password:
                        st.error("Completa todos los campos")
                    else:
                        user = auth_db.authenticate(username, password)
                        if user:
                            login_user(user)
                            st.rerun()
                        else:
                            st.error("Credenciales incorrectas")

                if reg_btn:
                    st.session_state.mostrar_registro = True
                    st.rerun()

            st.markdown(
                """
            <div class="auth-footer">
                <p>🛡️SAFE Inteligencia Segura</p>
            </div>
            </div>
            """,
                unsafe_allow_html=True,
            )


def page_registro():
    inject_styles()

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container():
            st.markdown('<div class="auth-container">', unsafe_allow_html=True)

            st.markdown(
                """
            <div class="auth-logo">
                <div class="shield">🛡️</div>
                <h2>Crear Cuenta</h2>
                <p>Únete a SAFE</p>
            </div>
            """,
                unsafe_allow_html=True,
            )

            with st.form("registro_form", clear_on_submit=True):
                username = st.text_input("Usuario", placeholder="Nombre de usuario")
                email = st.text_input("Email", placeholder="correo@email.com")
                nombre = st.text_input("Nombre", placeholder="Tu nombre (opcional)")
                password = st.text_input(
                    "Contraseña", type="password", placeholder="••••••••"
                )
                password_confirm = st.text_input(
                    "Confirmar", type="password", placeholder="••••••••"
                )

                c1, c2 = st.columns(2)
                with c1:
                    submit = st.form_submit_button(
                        "Registrarse", use_container_width=True
                    )
                with c2:
                    login_btn = st.form_submit_button(
                        "Ya tengo cuenta", use_container_width=True
                    )

                if submit:
                    if not username or not email or not password:
                        st.error("Campos obligatorios")
                    elif len(password) < 6:
                        st.error("Mínimo 6 caracteres")
                    elif password != password_confirm:
                        st.error("Las contraseñas no coinciden")
                    else:
                        user = auth_db.create_user(username, email, password, nombre)
                        if user:
                            st.success("¡Cuenta creada!")
                            st.session_state.mostrar_registro = False
                            st.rerun()
                        else:
                            st.error("Usuario o email ya existe")

                if login_btn:
                    st.session_state.mostrar_registro = False
                    st.rerun()

            st.markdown(
                """
            <div class="auth-footer">
                <p>© 2026 SAFE Inteligencia Segura</p>
            </div>
            </div>
            """,
                unsafe_allow_html=True,
            )


def page_perfil():
    if not st.session_state.get("logged_in"):
        st.warning("Debes iniciar sesión")
        page_login()
        st.stop()

    user_id = st.session_state.get("user_id")
    user = auth_db.get_user_by_id(user_id)

    if user:
        st.title("Mi Perfil")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Usuario:** {user.get('username')}")
            st.markdown(f"**Email:** {user.get('email')}")
        with col2:
            st.markdown(f"**Nombre:** {user.get('nombre')}")
            st.markdown(f"**Rol:** {user.get('rol')}")
