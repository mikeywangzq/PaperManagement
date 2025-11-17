"""Authentication and authorization module."""
import streamlit as st
import yaml
from pathlib import Path
from typing import Optional, Dict, Any
import hashlib


def hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def load_auth_config() -> Dict[str, Any]:
    """
    Load authentication configuration from users.yaml.

    Returns:
        Dictionary containing user credentials and settings
    """
    config_path = Path(__file__).parent.parent / "config" / "users.yaml"

    if not config_path.exists():
        # Create default config if not exists
        default_config = {
            "credentials": {
                "usernames": {
                    "admin": {
                        "name": "Administrator",
                        "password": hash_password("admin123"),  # Default password
                        "role": "admin"
                    },
                    "demo": {
                        "name": "Demo User",
                        "password": hash_password("demo123"),  # Default password
                        "role": "user"
                    }
                }
            },
            "cookie": {
                "name": "ai_paper_management",
                "key": "random_signature_key_123",
                "expiry_days": 30
            },
            "preauthorized": {
                "emails": []
            }
        }

        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)

    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def check_authentication() -> bool:
    """
    Check if user is authenticated.

    Returns:
        True if authenticated, False otherwise
    """
    return st.session_state.get("authentication_status", False)


def get_current_user() -> Optional[Dict[str, Any]]:
    """
    Get current authenticated user information.

    Returns:
        Dictionary containing user info or None if not authenticated
    """
    if not check_authentication():
        return None

    return {
        "username": st.session_state.get("username"),
        "name": st.session_state.get("name"),
        "role": st.session_state.get("role", "user")
    }


def login_page():
    """
    Display login page and handle authentication.

    Returns:
        True if authentication successful
    """
    st.set_page_config(page_title="Login", page_icon="🔐", layout="centered")

    st.markdown("""
        <style>
        .login-container {
            max-width: 400px;
            margin: 0 auto;
            padding: 2rem;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="login-container">', unsafe_allow_html=True)

    st.title("🔐 Login")
    st.markdown("---")

    # Load auth config
    config = load_auth_config()

    # Login form
    with st.form("login_form"):
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        submit = st.form_submit_button("Login")

        if submit:
            if not username or not password:
                st.error("Please enter both username and password")
            else:
                # Check credentials
                users = config["credentials"]["usernames"]

                if username in users:
                    stored_password = users[username]["password"]
                    input_password_hash = hash_password(password)

                    if stored_password == input_password_hash:
                        # Authentication successful
                        st.session_state.authentication_status = True
                        st.session_state.username = username
                        st.session_state.name = users[username]["name"]
                        st.session_state.role = users[username].get("role", "user")
                        st.success(f"Welcome {users[username]['name']}!")
                        st.rerun()
                    else:
                        st.error("Incorrect password")
                else:
                    st.error("Username not found")

    st.markdown('</div>', unsafe_allow_html=True)

    # Default credentials info
    with st.expander("ℹ️ Default Credentials"):
        st.info("""
        **Demo Accounts:**

        Admin Account:
        - Username: `admin`
        - Password: `admin123`

        User Account:
        - Username: `demo`
        - Password: `demo123`

        **Note:** Please change these default passwords in production!
        """)

    return False


def logout():
    """Logout current user."""
    st.session_state.authentication_status = False
    st.session_state.username = None
    st.session_state.name = None
    st.session_state.role = None


def require_authentication(func):
    """
    Decorator to require authentication for a function.

    Usage:
        @require_authentication
        def my_page():
            st.write("Protected content")
    """
    def wrapper(*args, **kwargs):
        if not check_authentication():
            login_page()
            return None
        return func(*args, **kwargs)
    return wrapper


def check_permission(required_role: str = "user") -> bool:
    """
    Check if current user has required role.

    Args:
        required_role: Required role ("user" or "admin")

    Returns:
        True if user has permission
    """
    user = get_current_user()
    if not user:
        return False

    role_hierarchy = {"admin": 2, "user": 1}
    user_level = role_hierarchy.get(user.get("role", "user"), 0)
    required_level = role_hierarchy.get(required_role, 1)

    return user_level >= required_level


def display_user_info():
    """Display current user info in sidebar."""
    user = get_current_user()
    if user:
        with st.sidebar:
            st.markdown("---")
            st.markdown("### 👤 User Info")
            st.info(f"""
            **Name:** {user['name']}

            **Username:** {user['username']}

            **Role:** {user['role'].upper()}
            """)

            if st.button("🚪 Logout"):
                logout()
                st.rerun()
