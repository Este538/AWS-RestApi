from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import boto3
from uuid import uuid4
import time
import random
import string

# Configuración del router
router = APIRouter()

# Configuración de la base de datos SQL (MySQL en este caso)
DATABASE_URL = "mysql+mysqlconnector://admin:lab-password@lab.cdimoeeaodmy.us-east-1.rds.amazonaws.com:3306/lab"
#DATABASE_URL = "mysql+mysqlconnector://root:@localhost:3306/aws"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelo de base de datos
class Alumnos(Base):
    __tablename__ = "Alumnos"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    nombres = Column(String(50), nullable=False)
    apellidos = Column(String(50), nullable=False)
    matricula = Column(String(50), unique=True, nullable=False)
    promedio = Column(Float, nullable=False)
    fotoPerfilUrl = Column(String(255))
    password = Column(String(50), nullable=False)

Base.metadata.create_all(bind=engine)

# Esquema de Pydantic
class Alumno(BaseModel):
    id: Optional[int]
    nombres: str = Field(..., max_length=50)
    apellidos: str = Field(..., max_length=50)
    matricula: str = Field(..., max_length=50)
    promedio: float
    fotoPerfilUrl: str = Field(None, max_length=255)
    password: str = Field(..., max_length=50)

    class Config:
        orm_mode = True

# Dependencia para la sesión de SQLAlchemy
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Configuración de DynamoDB
AWS_ACCESS_KEY_ID = "ASIA6OJNRNDT5OP4MQIN"
AWS_SECRET_ACCESS_KEY = "H3YTc5W5m15Ei0Gk8vheNEVKzz0NIRgbCqFHl1Nk"
AWS_SESSION_TOKEN = "IQoJb3JpZ2luX2VjENn//////////wEaCXVzLXdlc3QtMiJHMEUCIQC3FEABhzaHR+qqKp7gP3Lw/TfV7d/pIegSfch4WK8M/QIgMua0t+8bI2tKAMfAEW4zOP8Hu5Z1oEjcma/xrM+Ic+UqwwIIkf//////////ARAAGgw5OTI3Njk4MjkwOTUiDFr2eGPvshu/vxkROCqXAi4jwaTQ5bESYAxgvPfM0U0bhM3wx5tjE7tsxOflHeLRPnnKIQpgVV3eC2glJQKzTGd9umh0BDKWSM8U0KDxQg8XhTZ6jIROdLU3apx3JcYDhweL1wQ8mK6Q1GekHo72UuiZQqsz1NXdXPifgvx+j7oyXCFQ1hlIiRgGckm4dtCRXUGYyZmReflz8bpQV/cK+NVOlfIFib4de53HXgyaCrkCT7lEv8yJrE+a1aEfHosfsG7Uq5tZ+ISu88qjxvf61puewvRY/kmNKzDTpOFZtDsnZFZar9gD0cem5uN6ycYP5ggzvciItVy3sfE0CMXhLH9/X6/GkG8vEbfp+pBK55jdEqmRO58kwucrRrrJH1HWByZm+grOYjDc1OG6BjqdAecuNZcjN55V/OqPpae0kjtv7yQEBhrnJ10tlDvQOd6naAf7VE50J4+d+zHHV9DIokTbjUKCyOla5BeFKo5iwQ0b0IzG08ANpjDhxhm1WTEvzvxaN2SfZ4yub6NqcGNPW/Z39O28UU7xqynoJH4jXEWxpu6J28Ui1v/7afoeGLyz0GyO9AZsLC9ei4S7pd2lVdmD97CxQ7gITONO9MU="
REGION_NAME = "us-east-1"

# Crear la sesión y cliente
session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN,
    region_name=REGION_NAME
)
client = session.client('dynamodb')

# Modelo de datos para el login
class LoginRequest(BaseModel):
    password: str

# Generar un sessionString aleatorio
def generar_session_string():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=128))

@router.post("/alumnos/{id}/session/login")
async def login(id: int, request: LoginRequest, db: Session = Depends(get_db)):
    # Buscar al alumno en la base de datos por ID
    alumno = db.query(Alumnos).filter(Alumnos.id == id).first()
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")

    # Comparar la contraseña proporcionada con la almacenada
    if alumno.password != request.password:  # Se asume que `alumno.password` contiene la contraseña
        raise HTTPException(status_code=400, detail="Contraseña incorrecta")

    # Generar una nueva sesión para el alumno
    session_string = generar_session_string()
    timestamp = int(time.time())

    # Simular el almacenamiento de la sesión en una tabla (por ejemplo, `Sesiones`)
    nueva_sesion = {
        'id': {'S': str(uuid4())},  # Debe estar dentro de un diccionario con clave 'S' para string
        'alumnoId': {'N': str(id)},  # Para el ID, 'N' indica que es un número (como string)
        'fecha': {'N': str(timestamp)},  # La fecha debe ser un número (como string)
        'active': {'BOOL': True},  # 'BOOL' es el tipo para un valor booleano
        'sessionString': {'S': session_string}  # Para el sessionString, debe estar como string
    }
    table_name = 'sesiones-alumnos'
    try:
        response = client.put_item(
            TableName=table_name,
            Item=nueva_sesion
        )
        print("Datos subidos correctamente:", response)
    except Exception as e:
        print("Error al subir los datos:", e)


# Endpoint para verificar sesión en DynamoDB
@router.post("/alumnos/{id}/session/verify")
async def verify(id: int, session_string: str):
    # Realizar la consulta a DynamoDB para buscar la sesión
    response = client.scan(
        FilterExpression="alumnoId = :alumnoId AND sessionString = :sessionString",
        ExpressionAttributeValues={
            ':alumnoId': str(id),
            ':sessionString': session_string
        }
    )
    
    # Obtener los resultados
    items = response.get('Items', [])
    
    # Si no se encuentra la sesión, lanzar un error
    if not items:
        raise HTTPException(status_code=400, detail="Sesión no válida")
    
    # Verificar si la sesión está activa
    session = items[0]
    if session.get('active', False):  # Asegurarse de que la sesión esté activa
        return {"message": "Sesión válida"}
    
    # Si la sesión no está activa, lanzar un error
    raise HTTPException(status_code=400, detail="Sesión inactiva")

# Endpoint para logout
@router.post("/alumnos/{id}/session/logout")
async def logout(id: int, session_string: str):
    response = client.scan(
        FilterExpression="alumnoId = :alumnoId AND sessionString = :sessionString",
        ExpressionAttributeValues={
            ':alumnoId': str(id),
            ':sessionString': session_string
        }
    )
    items = response.get('Items', [])
    if not items:
        raise HTTPException(status_code=400, detail="Sesión no válida")
    session = items[0]
    client.update_item(
        Key={'id': session['id']},
        UpdateExpression="SET active = :active",
        ExpressionAttributeValues={':active': False}
    )
    return {"message": "Sesión cerrada exitosamente"}

# Endpoints
@router.get("/alumnos", response_model=list[Alumno])
async def get_alumnos(db: Session = Depends(get_db)):
    return db.query(Alumnos).all()

@router.get("/alumnos/{id}", response_model=Alumno)
async def get_alumno(id: int, db: Session = Depends(get_db)):
    alumno = db.query(Alumnos).filter(Alumnos.id == id).first()
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    return alumno

@router.post("/alumnos", response_model=Alumno, status_code=201)
async def crear_alumno(alumno: Alumno, db: Session = Depends(get_db)):
    db_alumno = Alumnos(**alumno.dict())
    try:
        db.add(db_alumno)
        db.commit()
        db.refresh(db_alumno)
        return db_alumno
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al guardar el alumno: " + str(e))

@router.put("/alumnos/{id}", response_model=Alumno)
async def actualizar_alumno(id: int, alumno_recibido: Alumno, db: Session = Depends(get_db)):
    # Fetch the existing alumno
    alumno = db.query(Alumnos).filter(Alumnos.id == id).first()
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")

    # Update alumno attributes
    for key, value in alumno_recibido.dict(exclude_unset=True).items():  # Exclude unset to avoid overwriting with None
        setattr(alumno, key, value)

    try:
        # Commit changes to the database
        db.commit()
        db.refresh(alumno)
    except Exception as e:
        # Rollback on failure and raise HTTPException with error details
        db.rollback()
        raise HTTPException(status_code=404, detail=f"Error al actualizar alumno: {str(e)}")

    return alumno  # Return the updated alumno

@router.delete("/alumnos/{id}", response_model=Alumno)
async def eliminar_alumno(id: int, db: Session = Depends(get_db)):
    # Fetch the existing alumno
    alumno = db.query(Alumnos).filter(Alumnos.id == id).first()
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")

    try:
        # Delete alumno from the database
        db.delete(alumno)
        db.commit()
    except Exception as e:
        # Rollback on failure and raise HTTPException with error details
        db.rollback()
        return {"message": "Alumno eliminado"}

    raise HTTPException(status_code=404, detail="Alumno no encontrado")
