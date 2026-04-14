"""
🛡️ SAFE - Sistema de Autenticación
=============================

Módulo de autenticación para SAFE - Motor de Predicción de Eventos

Autor: SAFE Inteligencia Segura
Versión: 1.0.0
"""

import streamlit as st
import pandas as pd
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

    def delete_user(self, user_id: str) -> bool:
        users = self._read()
        initial = len(users)
        users = [u for u in users if u.get("id") != user_id]
        if len(users) < initial:
            self._write(users)
            return True
        return False


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
        layout="centered",
    )

    st.markdown(
        """
    <style>
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 30px;
        background: #f5f5f5;
        border-radius: 15px;
    }
    .safe-logo {
        text-align: center;
        font-size: 48px;
        margin-bottom: 20px;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
    <div class="safe-logo">🛡️</div>
    <h1 style="text-align: center;">SAFE</h1>
    <h3 style="text-align: center; color: #666;">Motor de Predicción de Eventos</h3>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    with st.form("login_form", clear_on_submit=True):
        username = st.text_input(
            "Usuario o Email", placeholder="Ingrese su usuario o correo"
        )
        password = st.text_input(
            "Contraseña", type="password", placeholder="Ingrese su contraseña"
        )

        col1, col2 = st.columns([1, 1])
        with col1:
            submit = st.form_submit_button(
                "🔐 Iniciar Sesión", type="primary", use_container_width=True
            )
        with col2:
            registro_btn = st.form_submit_button(
                "📝 Registrarse", use_container_width=True
            )

        if submit:
            if not username or not password:
                st.error("⚠️ Complete todos los campos")
            else:
                user = auth_db.authenticate(username, password)
                if user:
                    login_user(user)
                    st.success("✅ Iniciando sesión...")
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos")

        if registro_btn:
            st.switch_page("page_registro")

    st.markdown("---")
    st.markdown(
        """
    <div style="text-align: center; color: #888; font-size: 12px;">
        🛡️ SAFE - Motor de Predicción de Eventos<br>
        © 2026 SAFE Inteligencia Segura
    </div>
    """,
        unsafe_allow_html=True,
    )


def page_registro():
    st.set_page_config(
        page_title="SAFE - Registrarse",
        page_icon="🛡️",
        layout="centered",
    )

    st.markdown(
        """
    <style>
    .registro-container {
        max-width: 450px;
        margin: 0 auto;
        padding: 30px;
        background: #f5f5f5;
        border-radius: 15px;
    }
    .safe-logo {
        text-align: center;
        font-size: 48px;
        margin-bottom: 20px;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
    <div class="safe-logo">🛡️</div>
    <h1 style="text-align: center;">SAFE</h1>
    <h3 style="text-align: center; color: #666;">Registro de Usuario</h3>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    with st.form("registro_form", clear_on_submit=True):
        username = st.text_input(
            "Usuario *",
            placeholder="Nombre de usuario (único)",
        )
        email = st.text_input(
            "Email *",
            placeholder="correo@ejemplo.com",
        )
        nombre = st.text_input(
            "Nombre Completo",
            placeholder="Tu nombre (opcional)",
        )
        password = st.text_input(
            "Contraseña *", type="password", placeholder="Mínimo 6 caracteres"
        )
        password_confirm = st.text_input(
            "Confirmar Contraseña *",
            type="password",
            placeholder="Repita la contraseña",
        )

        st.markdown(
            "*Los campos marcados con * son requeridos*", unsafe_allow_html=True
        )

        col1, col2 = st.columns([1, 1])
        with col1:
            submit = st.form_submit_button(
                "📝 Registrarse", type="primary", use_container_width=True
            )
        with col2:
            login_btn = st.form_submit_button(
                "🔐 Ya tengo cuenta", use_container_width=True
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
                    st.success("✅ ¡Registro exitoso! Ahora puede iniciar sesión")
                    st.info("Serás redirigido al login...")
                    st.switch_page("page_login")
                else:
                    st.error("❌ El usuario o email ya están registrados")

        if login_btn:
            st.switch_page("page_login")

    st.markdown("---")
    if st.button("← Volver al Login"):
        st.switch_page("page_login")

    st.markdown(
        """
    <div style="text-align: center; color: #888; font-size: 12px;">
        🛡️ SAFE - Motor de Predicción de Eventos<br>
        © 2026 SAFE Inteligencia Segura
    </div>
    """,
        unsafe_allow_html=True,
    )


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
