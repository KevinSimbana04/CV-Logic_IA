from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime

# ==========================================
# USUARIOS Y AUTENTICACIÓN
# ==========================================
class RegistroUsuario(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(..., min_length=6)
    rol: str = Field(..., pattern="^(empresa|candidato)$")
    nombre_completo: str = Field(...)

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
    fecha_creacion: datetime
    empresa: Optional[UsuarioOut] = None

    class Config:
        from_attributes = True

# ==========================================
# POSTULACIONES
# ==========================================
class PostulacionOut(BaseModel):
    id: int
    candidato_id: int
    vacante_id: int
    fecha_postulacion: datetime
    vacante: Optional[VacanteOut] = None

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
    es_top_3: bool
    rol_sugerido_por_ia: Optional[str] = None
    porcentaje_rol_sugerido: Optional[str] = None
    confianza_rol_sugerido: Optional[float] = None

class MatchResponseOut(BaseModel):
    resultados: List[MatchCandidatoOut] = []

# ==========================================
# ENTRENAMIENTO IA
# ==========================================
class TrainingParams(BaseModel):
    hidden_layers: str = Field(default="128,64", description="Capas ocultas separadas por coma, ej: 128,64")
    max_iter: int = Field(default=300, description="Número máximo de iteraciones (épocas)")
    activation: str = Field(default="relu", pattern="^(identity|logistic|tanh|relu)$", description="Función de activación")

class TrainingMetricsOut(BaseModel):
    mensaje: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float