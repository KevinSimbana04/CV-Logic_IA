from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt

import os
from dotenv import load_dotenv

# Cargar variables del archivo .env
load_dotenv()

# ==========================================
# CONFIGURACIÓN DE SEGURIDAD
# ==========================================
SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES"))

# Configuración del motor de encriptación
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ==========================================
# FUNCIONES DE CONTRASEÑAS
# ==========================================
def obtener_password_hash(password: str) -> str:
    """Toma la contraseña en texto plano y devuelve el hash encriptado."""
    return pwd_context.hash(password)

def verificar_password(plain_password: str, hashed_password: str) -> bool:
    """Compara la contraseña ingresada en el login con el hash de la base de datos."""
    return pwd_context.verify(plain_password, hashed_password)

# ==========================================
# GENERACIÓN DE TOKENS (JWT)
# ==========================================
def crear_token_acceso(data: dict, expires_delta: timedelta | None = None) -> str:
    """Crea y firma un token JWT insertando los datos (como el email y el rol)."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Tiempo por defecto si no se especifica uno
        expire = datetime.utcnow() + timedelta(minutes=15)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt
