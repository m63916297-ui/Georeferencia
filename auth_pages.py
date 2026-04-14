"""
🛡️ SAFE - Autenticación Minimalista
=============================

Diseño minimalista alto contraste para SAFE
Negro sobre blanco

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
            if u.get("username") == username or u.get("email") == email:
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
    for key in [
        "user_id",
        "username",
        "user_email",
        "user_nombre",
        "user_rol",
        "logged_in",
        "mostrar_registro",
    ]:
        if key not in st.session_state:
            st.session_state[key] = None if "logged" in key else False


def login_user(user: Dict):
    for k, v in [
        ("user_id", user.get("id")),
        ("username", user.get("username")),
        ("user_email", user.get("email")),
        ("user_nombre", user.get("nombre")),
        ("user_rol", user.get("rol")),
        ("logged_in", True),
    ]:
        st.session_state[k] = v


def logout_user():
    st.session_state.logged_in = False


def render_auth_sidebar():
    if st.session_state.get("logged_in"):
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"**{st.session_state.get('user_nombre', 'Usuario')}**")
        st.sidebar.markdown(f"_{st.session_state.get('username', '')}_")
        if st.sidebar.button("Cerrar Sesión", use_container_width=True):
            logout_user()
            st.rerun()


def inject_styles():
    st.markdown(
        """
    <style>
    /* Fondo blanco */
    .stApp { background: #FFFFFF !important; }
    
    /* Contenedor */
    .auth-box {
        width: 320px;
        margin: 60px auto;
        background: #FFFFFF;
        border: 2px solid #000000;
    }
    
    /* Logo */
    .auth-logo { text-align: center; margin-bottom: 24px; }
    .auth-logo .shield {
        width: 44px; height: 44px;
        background: #000000;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
        margin-bottom: 10px;
    }
    .auth-logo h2 {
        color: #000000; font-size: 20px;
        font-weight: 700; margin: 0;
    }
    .auth-logo p {
        color: #666666; font-size: 12px; margin: 0;
    }
    
    /* Inputs */
    .auth-box .stTextInput > div > div {
        border: 2px solid #000000;
        background: #FFFFFF;
        border-radius: 0;
    }
    .auth-box .stTextInput > div > div:focus-within {
        border-color: #000000;
    }
    .auth-box .stTextInput label {
        font-size: 11px; font-weight: 600; color: #000000;
    }
    .auth-box input::placeholder { color: #999999; }
    
    /* Botones */
    .auth-box .stButton > button[kind="primary"] {
        background: #000000 !important;
        border: 2px solid #000000 !important;
        border-radius: 0 !important;
        padding: 12px !important;
        font-weight: 600 !important;
        font-size: 12px !important;
    }
    .auth-box .stButton > button:not([kind="primary"]) {
        background: #FFFFFF !important;
        border: 2px solid #000000 !important;
        border-radius: 0 !important;
        color: #000000 !important;
        font-weight: 600 !important;
    }
    
    /* Footer */
    .auth-ft { text-align: center; margin-top: 16px; color: #999999; font-size: 10px; }
    </style>
    """,
        unsafe_allow_html=True,
    )


def page_login():
    inject_styles()
    st.markdown('<div class="auth-box">', unsafe_allow_html=True)

    st.markdown(
        """
    <div class="auth-logo">
        <div class="shield">🛡️</div>
        <h2>SAFE</h2>
        <p>Motor de Predicción</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    with st.form("login", clear_on_submit=True):
        u = st.text_input("Usuario / Email", placeholder="user@email.com")
        p = st.text_input("Contraseña", type="password", placeholder="••••••")

        c1, c2 = st.columns(2)
        with c1:
            s = st.form_submit_button("Entrar", use_container_width=True)
        with c2:
            r = st.form_submit_button("Crear cuenta", use_container_width=True)

        if s:
            if not u or not p:
                st.error("Complete campos")
            else:
                u = auth_db.authenticate(u, p)
                if u:
                    login_user(u)
                    st.rerun()
                else:
                    st.error("Credenciales inválidas")
        if r:
            st.session_state.mostrar_registro = True
            st.rerun()

    st.markdown(
        '<div class="auth-ft">SAFE Inteligencia Segura</div></div>',
        unsafe_allow_html=True,
    )


def page_registro():
    inject_styles()
    st.markdown('<div class="auth-box">', unsafe_allow_html=True)

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

    with st.form("reg", clear_on_submit=True):
        u = st.text_input("Usuario", placeholder="username")
        e = st.text_input("Email", placeholder="user@mail.com")
        n = st.text_input("Nombre", placeholder="Tu nombre")
        p = st.text_input("Contraseña", type="password", placeholder="••••••")
        pc = st.text_input("Confirmar", type="password", placeholder="••••••")

        c1, c2 = st.columns(2)
        with c1:
            s = st.form_submit_button("Registrar", use_container_width=True)
        with c2:
            l = st.form_submit_button("Ya tengo cuenta", use_container_width=True)

        if s:
            if not u or not e or not p:
                st.error("Campos obligatorios")
            elif len(p) < 6:
                st.error("Mín 6 caracteres")
            elif p != pc:
                st.error("No coinciden")
            else:
                if auth_db.create_user(u, e, p, n):
                    st.success("Cuenta creada")
                    st.session_state.mostrar_registro = False
                    st.rerun()
                else:
                    st.error("Usuario o email existe")
        if l:
            st.session_state.mostrar_registro = False
            st.rerun()

    st.markdown('<div class="auth-ft">© 2026 SAFE</div></div>', unsafe_allow_html=True)


def page_perfil():
    if not st.session_state.get("logged_in"):
        page_login()
        st.stop()
    u = auth_db.get_user_by_id(st.session_state.user_id)
    if u:
        st.title("Mi Perfil")
        st.markdown(f"**Usuario:** {u.get('username')}")
        st.markdown(f"**Email:** {u.get('email')}")
        st.markdown(f"**Nombre:** {u.get('nombre')}")
