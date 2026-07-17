from sqlalchemy import Column, Integer, String, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.orm import relationship
from data.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    rol = Column(String, nullable=False)
    nombre_completo = Column(String, nullable=False)

    perfil = relationship("PerfilCandidato", back_populates="usuario", uselist=False)
    vacantes = relationship("Vacante", back_populates="empresa")
    postulaciones = relationship("Postulacion", back_populates="candidato")

class PerfilCandidato(Base):
    __tablename__ = "perfil_candidato"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), unique=True, nullable=False)
    tecnologias = Column(JSON, nullable=False)
    anios_experiencia = Column(Integer, nullable=False)
    modalidad = Column(String, nullable=False)
    tipo_empleo = Column(String, nullable=False, default="Full-Time")

    usuario = relationship("Usuario", back_populates="perfil")

class Vacante(Base):
    __tablename__ = "vacantes"

    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    titulo_oferta = Column(String, nullable=False)
    tecnologias_requeridas = Column(JSON, nullable=False)
    nivel_experiencia_esperado = Column(Integer, nullable=False)
    modalidad = Column(String, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    empresa = relationship("Usuario", back_populates="vacantes")
    postulaciones = relationship("Postulacion", back_populates="vacante")

class Postulacion(Base):
    __tablename__ = "postulaciones"

    id = Column(Integer, primary_key=True, index=True)
    candidato_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    vacante_id = Column(Integer, ForeignKey("vacantes.id"), nullable=False)
    fecha_postulacion = Column(DateTime, default=datetime.utcnow)

    candidato = relationship("Usuario", back_populates="postulaciones")
    vacante = relationship("Vacante", back_populates="postulaciones")