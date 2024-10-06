#models.py
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String
import os

baseDatos = os.getenv('baseDatos')
engine = create_engine(baseDatos)
Session = sessionmaker(bind=engine)

class CustomBase:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

Base = declarative_base(cls=CustomBase)

class Tutor(Base):
    __table_args__ = {'schema': 'becas'}
    __tablename__ = 'tutores'
    id = Column(Integer, primary_key=True)
    nombre = Column(String)
    correo = Column(String)
    identificador = Column(String)

    def __repr__(self):
        return f"<Tutor {self.nombre}>"

class Alumno(Base):
    __table_args__ = {'schema': 'becas'}
    __tablename__ = 'alumnos'
    cuenta = Column(Integer, primary_key=True)
    nombre = Column(String)
    p_apellido = Column(String)
    s_apellido = Column(String)

    def __repr__(self):
        return f"<Alumno {self.nombre} cuenta {self.cuenta}>"

class ApoyoAlimenticio(Base):
    __table_args__ = {'schema': 'becas'}
    __tablename__ = 'apoyo_alimenticio'
    id = Column(Integer, primary_key=True)
    cuenta = Column(Integer)
    prioridad = Column(Integer)
    comentarios = Column(String)
    tutor = Column(Integer, ForeignKey('becas.tutores.id'))  # Referencia correcta al esquema y tabla

    def __repr__(self):
        return f"<ApoyoAlimenticio {self.id} para cuenta {self.cuenta}>"
