from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List
from jose import jwt, JWTError

# Importaciones locales
from data.database import engine, Base, get_db
from models.models import Usuario, PerfilCandidato, Vacante
from schemas import (
    RegistroUsuario, TokenAuth, PerfilCandidatoCreate, PerfilCandidatoOut,
    VacanteCreate, VacanteOut, MatchCandidatoOut, MatchResponseOut, UsuarioOut
)
from jwt.security import obtener_password_hash, verificar_password, crear_token_acceso, SECRET_KEY, ALGORITHM
from services.ai_service import evaluar_candidatos_para_vacante


app = FastAPI(title="CV-Logic AI: B2B Matchmaking", version="2.0.0")

# Configuración JWT
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def obtener_usuario_actual(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if usuario is None:
        raise credentials_exception
    return usuario

def obtener_candidato_actual(usuario: Usuario = Depends(obtener_usuario_actual)):
    if usuario.rol != "candidato":
        raise HTTPException(status_code=403, detail="Rol de candidato requerido")
    return usuario

def obtener_empresa_actual(usuario: Usuario = Depends(obtener_usuario_actual)):
    if usuario.rol != "empresa":
        raise HTTPException(status_code=403, detail="Rol de empresa requerido")
    return usuario

# ==========================================
# ROUTER: AUTH
# ==========================================
auth_router = APIRouter(prefix="/auth", tags=["Autenticación"])

@auth_router.post("/registro", status_code=status.HTTP_201_CREATED)
def registrar_usuario(usuario: RegistroUsuario, db: Session = Depends(get_db)):
    if db.query(Usuario).filter(Usuario.email == usuario.email).first():
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    
    nuevo_usuario = Usuario(
        email=usuario.email,
        hashed_password=obtener_password_hash(usuario.password),
        rol=usuario.rol,
        nombre_completo=usuario.nombre_completo
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return {"mensaje": "Usuario registrado exitosamente"}

@auth_router.post("/login", response_model=TokenAuth)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == form_data.username).first()
    if not usuario or not verificar_password(form_data.password, usuario.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    
    token = crear_token_acceso(data={"sub": usuario.email, "rol": usuario.rol})
    return {"access_token": token, "token_type": "bearer"}

# ==========================================
# ROUTER: CANDIDATOS
# ==========================================
candidatos_router = APIRouter(prefix="/candidatos", tags=["Candidatos"])

@candidatos_router.post("/perfil", status_code=status.HTTP_201_CREATED, response_model=PerfilCandidatoOut)
def guardar_perfil(perfil: PerfilCandidatoCreate, usuario=Depends(obtener_candidato_actual), db: Session = Depends(get_db)):
    perfil_db = db.query(PerfilCandidato).filter(PerfilCandidato.usuario_id == usuario.id).first()
    
    if perfil_db:
        # Actualizar perfil existente
        perfil_db.tecnologias = perfil.tecnologias
        perfil_db.anios_experiencia = perfil.anios_experiencia
        perfil_db.modalidad = perfil.modalidad
        perfil_db.tipo_empleo = perfil.tipo_empleo
    else:
        # Crear nuevo perfil
        perfil_db = PerfilCandidato(
            usuario_id=usuario.id,
            tecnologias=perfil.tecnologias,
            anios_experiencia=perfil.anios_experiencia,
            modalidad=perfil.modalidad,
            tipo_empleo=perfil.tipo_empleo
        )
        db.add(perfil_db)
        
    db.commit()
    db.refresh(perfil_db)
    return perfil_db

@candidatos_router.get("/perfil", response_model=PerfilCandidatoOut)
def ver_perfil(usuario=Depends(obtener_candidato_actual), db: Session = Depends(get_db)):
    perfil = db.query(PerfilCandidato).filter(PerfilCandidato.usuario_id == usuario.id).first()
    if not perfil:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")
    return perfil

# ==========================================
# ROUTER: EMPRESAS
# ==========================================
empresas_router = APIRouter(prefix="/empresas", tags=["Empresas y Reclutadores"])

@empresas_router.post("/vacantes", status_code=status.HTTP_201_CREATED, response_model=VacanteOut)
def crear_vacante(vacante: VacanteCreate, usuario=Depends(obtener_empresa_actual), db: Session = Depends(get_db)):
    nueva_vacante = Vacante(
        empresa_id=usuario.id,
        titulo_oferta=vacante.titulo_oferta,
        tecnologias_requeridas=vacante.tecnologias_requeridas,
        nivel_experiencia_esperado=vacante.nivel_experiencia_esperado,
        modalidad=vacante.modalidad
    )
    db.add(nueva_vacante)
    db.commit()
    db.refresh(nueva_vacante)
    return nueva_vacante

@empresas_router.get("/vacantes", response_model=List[VacanteOut])
def listar_vacantes(usuario=Depends(obtener_empresa_actual), db: Session = Depends(get_db)):
    vacantes = db.query(Vacante).filter(Vacante.empresa_id == usuario.id).all()
    return vacantes

@empresas_router.get("/vacantes/{id_vacante}/match", response_model=MatchResponseOut)
def obtener_matches(id_vacante: int, usuario=Depends(obtener_empresa_actual), db: Session = Depends(get_db)):
    vacante = db.query(Vacante).filter(Vacante.id == id_vacante, Vacante.empresa_id == usuario.id).first()
    if not vacante:
        raise HTTPException(status_code=404, detail="Vacante no encontrada")
        
    candidatos_activos = db.query(Usuario).filter(Usuario.rol == "candidato").all()
    
    # Procesar la IA
    try:
        resultados_ia = evaluar_candidatos_para_vacante(candidatos_activos, vacante.titulo_oferta)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en IA: {str(e)}")
        
    matches = []
    for res in resultados_ia:
        candidato = res["candidato"]
        matches.append(MatchCandidatoOut(
            candidato_id=candidato.id,
            nombre_completo=candidato.nombre_completo,
            email=candidato.email,
            perfil=candidato.perfil,
            porcentaje_match_vacante=f"{res['confianza_vacante']*100:.2f}%",
            confianza_vacante=res["confianza_vacante"],
            rol_sugerido_por_ia=res["rol_sugerido"],
            porcentaje_rol_sugerido=f"{res['confianza_sugerida']*100:.2f}%",
            confianza_rol_sugerido=res["confianza_sugerida"]
        ))
        
    # Obtener el top 5
    top_5 = matches[:5]
    
    if not top_5:
        return MatchResponseOut(candidato_ideal=None, otras_sugerencias=[])
        
    candidato_ideal = top_5[0]
    otras_sugerencias = top_5[1:]
        
    return MatchResponseOut(
        candidato_ideal=candidato_ideal,
        otras_sugerencias=otras_sugerencias
    )

# ==========================================
# INCLUIR ROUTERS EN LA APP
# ==========================================
app.include_router(auth_router)
app.include_router(candidatos_router)
app.include_router(empresas_router)