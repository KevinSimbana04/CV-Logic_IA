from fastapi import FastAPI, Depends, HTTPException, status, APIRouter, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List
from jose import jwt, JWTError
from datetime import datetime, timedelta

# Importaciones locales
from data.database import engine, Base, get_db
from models.models import Usuario, PerfilCandidato, Vacante, Postulacion
from schemas import (
    RegistroUsuario, TokenAuth, PerfilCandidatoCreate, PerfilCandidatoOut,
    VacanteCreate, VacanteOut, MatchCandidatoOut, MatchResponseOut, UsuarioOut, PostulacionOut,
    TrainingParams, TrainingMetricsOut
)
from jwt.security import obtener_password_hash, verificar_password, crear_token_acceso, SECRET_KEY, ALGORITHM
from services.ai_service import evaluar_candidatos_para_vacante
from services.training_service import entrenar_modelo_ia

# ==========================================
# RECREAR TABLAS EN DESARROLLO
# ==========================================
Base.metadata.create_all(bind=engine)

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

@auth_router.get("/me", response_model=UsuarioOut)
def obtener_perfil_actual(usuario: Usuario = Depends(obtener_usuario_actual)):
    return usuario

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

@candidatos_router.post("/vacantes/{id_vacante}/postular", status_code=status.HTTP_201_CREATED, response_model=PostulacionOut)
def postular_a_vacante(id_vacante: int, usuario=Depends(obtener_candidato_actual), db: Session = Depends(get_db)):
    vacante = db.query(Vacante).filter(Vacante.id == id_vacante).first()
    if not vacante:
        raise HTTPException(status_code=404, detail="Vacante no encontrada")
        
    # Verificar que no se haya postulado ya
    postulacion_previa = db.query(Postulacion).filter(Postulacion.candidato_id == usuario.id, Postulacion.vacante_id == id_vacante).first()
    if postulacion_previa:
        raise HTTPException(status_code=400, detail="Ya estás postulado a esta vacante")
        
    nueva_postulacion = Postulacion(
        candidato_id=usuario.id,
        vacante_id=id_vacante
    )
    db.add(nueva_postulacion)
    db.commit()
    db.refresh(nueva_postulacion)
    return nueva_postulacion

@candidatos_router.get("/vacantes", response_model=List[VacanteOut])
def listar_vacantes_disponibles(usuario=Depends(obtener_candidato_actual), db: Session = Depends(get_db)):
    return db.query(Vacante).all()

@candidatos_router.get("/postulaciones", response_model=List[PostulacionOut])
def listar_mis_postulaciones(usuario=Depends(obtener_candidato_actual), db: Session = Depends(get_db)):
    return db.query(Postulacion).filter(Postulacion.candidato_id == usuario.id).all()

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
        
    # Verificar tiempo de 3 minutos
    if vacante.fecha_creacion:
        tiempo_transcurrido = datetime.utcnow() - vacante.fecha_creacion
        if tiempo_transcurrido < timedelta(minutes=3):
            raise HTTPException(status_code=400, detail="La vacante sigue activa. El match solo se puede realizar 3 minutos después de su creación.")
            
    # Obtener solo los candidatos postulados
    postulaciones = db.query(Postulacion).filter(Postulacion.vacante_id == id_vacante).all()
    if not postulaciones:
        return MatchResponseOut(resultados=[])
        
    candidatos_postulados = [postulacion.candidato for postulacion in postulaciones]
    
    # Procesar la IA
    try:
        resultados_ia = evaluar_candidatos_para_vacante(candidatos_postulados, vacante.titulo_oferta)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en IA: {str(e)}")
        
    matches = []
    for res in resultados_ia:
        candidato = res["candidato"]
        
        porc_sugerido = f"{res['confianza_sugerida']*100:.2f}%" if res.get('confianza_sugerida') is not None else None
        
        matches.append(MatchCandidatoOut(
            candidato_id=candidato.id,
            nombre_completo=candidato.nombre_completo,
            email=candidato.email,
            perfil=candidato.perfil,
            porcentaje_match_vacante=f"{res['confianza_vacante']*100:.2f}%",
            confianza_vacante=res["confianza_vacante"],
            es_top_3=res.get("es_top_3", False),
            rol_sugerido_por_ia=res.get("rol_sugerido"),
            porcentaje_rol_sugerido=porc_sugerido,
            confianza_rol_sugerido=res.get("confianza_sugerida")
        ))
        
    return MatchResponseOut(resultados=matches)

# ==========================================
# ROUTER: IA (ENTRENAMIENTO)
# ==========================================
ia_router = APIRouter(prefix="/ia", tags=["Inteligencia Artificial"])

@ia_router.post("/entrenar")
def entrenar_ia(params: TrainingParams, background_tasks: BackgroundTasks, usuario=Depends(obtener_empresa_actual)):
    try:
        background_tasks.add_task(entrenar_modelo_ia, params)
        
        import json
        import os
        from services.training_service import MODELS_DIR
        
        metricas_anteriores = {}
        ruta_metricas = os.path.join(MODELS_DIR, 'last_metrics.json')
        if os.path.exists(ruta_metricas):
            with open(ruta_metricas, 'r') as file:
                metricas_anteriores = json.load(file)
                
        respuesta = {"mensaje": "Nuevo entrenamiento iniciado en segundo plano. Mostrando métricas del modelo actual."}
        respuesta.update(metricas_anteriores)
        
        return respuesta
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al iniciar el entrenamiento: {str(e)}")

@ia_router.get("/metricas")
def obtener_ultimas_metricas(usuario=Depends(obtener_empresa_actual)):
    import json
    import os
    from services.training_service import MODELS_DIR
    
    ruta_metricas = os.path.join(MODELS_DIR, 'last_metrics.json')
    if not os.path.exists(ruta_metricas):
        return {"mensaje": "Aún no hay entrenamientos previos."}
        
    with open(ruta_metricas, 'r') as file:
        metricas = json.load(file)
    return metricas

@ia_router.get("/matriz")
def obtener_matriz(usuario=Depends(obtener_empresa_actual)):
    import os
    from fastapi.responses import FileResponse
    from services.training_service import MODELS_DIR
    
    ruta_matriz = os.path.join(MODELS_DIR, 'confusion_matrix.png')
    if os.path.exists(ruta_matriz):
        return FileResponse(ruta_matriz, media_type="image/png")
    raise HTTPException(status_code=404, detail="Matriz de confusión no encontrada.")

# ==========================================
# RUTAS EN LA APP
# ==========================================
app.include_router(auth_router)
app.include_router(candidatos_router)
app.include_router(empresas_router)
app.include_router(ia_router)