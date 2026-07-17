from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

# ==========================================
# USUARIOS Y AUTENTICACIÓN
# ==========================================
class RegistroUsuario(BaseModel):
    email: EmailStr = Field(..., example="usuario@empresa.com")
    password: str = Field(..., min_length=6, example="Secreta123!")
    rol: str = Field(..., pattern="^(empresa|candidato)$", example="empresa")
    nombre_completo: str = Field(..., example="Tech Solutions S.A.")

class TokenAuth(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UsuarioOut(BaseModel):
    id: int
    email: EmailStr
    nombre_completo: str
    rol: str

    class Config:
        from_attributes = True

# ==========================================
# PERFIL DEL CANDIDATO
# ==========================================
class PerfilCandidatoCreate(BaseModel):
    tecnologias: List[str] = Field(...)
    anios_experiencia: int = Field(...)
    modalidad: str = Field(..., pattern="^(Remoto|Presencial|Híbrido)$")
    tipo_empleo: str = Field(default="Full-Time", pattern="^(Full-Time|Part-Time|Contract)$")

class PerfilCandidatoOut(PerfilCandidatoCreate):
    id: int
    usuario_id: int
    usuario: Optional[UsuarioOut] = None

    class Config:
        from_attributes = True

# ==========================================
# VACANTES (EMPRESA)
# ==========================================
class VacanteCreate(BaseModel):
    titulo_oferta: str = Field(...)
    tecnologias_requeridas: List[str] = Field(...)
    nivel_experiencia_esperado: int = Field(...)
    modalidad: str = Field(..., pattern="^(Remoto|Presencial|Híbrido)$")

class VacanteOut(VacanteCreate):
    id: int
    empresa_id: int
    empresa: Optional[UsuarioOut] = None

    class Config:
        from_attributes = True

# ==========================================
# RESULTADOS DE MATCH IA
# ==========================================
class MatchCandidatoOut(BaseModel):
    candidato_id: int
    nombre_completo: str
    email: str
    perfil: PerfilCandidatoOut
    porcentaje_match_vacante: str
    confianza_vacante: float
    rol_sugerido_por_ia: str
    porcentaje_rol_sugerido: str
    confianza_rol_sugerido: float

class MatchResponseOut(BaseModel):
    candidato_ideal: Optional[MatchCandidatoOut] = None
    otras_sugerencias: List[MatchCandidatoOut] = []