"""Authentication and authorization module."""
import streamlit as st
import yaml
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
import hashlib
import secrets


def hash_password(password: str, salt: str = None) -> Tuple[str, str]:
    """
    Hash a password using PBKDF2 with salt for better security.

    Args:
        password: Plain text password
        salt: Optional salt (generated if not provided)

    Returns:
        Tuple of (hashed_password, salt)
    """
    if salt is None:
        salt = secrets.token_hex(32)  # Generate 64-character hex salt

    # Use PBKDF2 with SHA-256 and 100,000 iterations
    password_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000  # Number of iterations
    ).hex()

    return password_hash, salt


def verify_password(password: str, stored_hash: str, salt: str) -> bool:
    """
    Verify a password against a stored hash.

    Args:
        password: Plain text password to verify
        stored_hash: Stored password hash
        salt: Salt used for hashing

    Returns:
        True if password matches, False otherwise
    """
    computed_hash, _ = hash_password(password, salt)
    return computed_hash == stored_hash


def load_auth_config() -> Dict[str, Any]:
    """
    Load authentication configuration from users.yaml.

    Returns:
        Dictionary containing user credentials and settings
    """
    config_path = Path(__file__).parent.parent / "config" / "users.yaml"

    if not config_path.exists():
        # Create default config with secure password hashing
        admin_hash, admin_salt = hash_password("admin123")
        demo_hash, demo_salt = hash_password("demo123")

        default_config = {
            "credentials": {
                "usernames": {
                    "admin": {
                        "name": "Administrator",
                        "password": admin_hash,
                        "salt": admin_salt,
                        "role": "admin"
                    },
                    "demo": {
                        "name": "Demo User",
                        "password": demo_hash,
                        "salt": demo_salt,
                        "role": "user"
                    }
                }
            },
            "cookie": {
                "name": "ai_paper_management",
                "key": secrets.token_hex(32),  # Generate random secure key
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

    Note: st.set_page_config() should be called by the main app before this function.

    Returns:
        True if authentication successful
    """
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
                    user_data = users[username]
                    stored_hash = user_data["password"]
                    salt = user_data.get("salt")

                    # Verify password
                    password_valid = False

                    if salt:
                        # New PBKDF2 hash with salt
                        password_valid = verify_password(password, stored_hash, salt)
                    else:
                        # Legacy SHA-256 hash (backward compatibility)
                        legacy_hash = hashlib.sha256(password.encode()).hexdigest()
                        password_valid = (stored_hash == legacy_hash)

                        if password_valid:
                            # Upgrade to PBKDF2 on successful login
                            new_hash, new_salt = hash_password(password)
                            users[username]["password"] = new_hash
                            users[username]["salt"] = new_salt

                            # Save updated config
                            config_path = Path(__file__).parent.parent / "config" / "users.yaml"
                            with open(config_path, 'w') as f:
                                yaml.dump(config, f, default_flow_style=False)

                    if password_valid:
                        # Authentication successful
                        st.session_state.authentication_status = True
                        st.session_state.username = username
                        st.session_state.name = user_data["name"]
                        st.session_state.role = user_data.get("role", "user")
                        st.success(f"Welcome {user_data['name']}!")
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
