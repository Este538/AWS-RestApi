from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Optional

# Configuración del router
router = APIRouter()

# Configuración de la base de datos
DATABASE_URL = "mysql+mysqlconnector://admin:lab-password@lab.cdimoeeaodmy.us-east-1.rds.amazonaws.com:3306/lab"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Modelo de base de datos
class Profesores(Base):
    __tablename__ = "Profesores"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    numeroEmpleado = Column(Integer, nullable=False)
    nombres = Column(String(50), nullable=False)
    apellidos = Column(String(50), nullable=False)
    horasClase = Column(Integer, nullable=False)

Base.metadata.create_all(bind=engine)

# Esquema de Pydantic
class Profesor(BaseModel):
    id: Optional[int]
    numeroEmpleado: int = Field(..., ge=0)
    nombres: str = Field(...,min_length=1)
    apellidos: str = Field(...,min_length=1)
    horasClase: int = Field(...,ge=0)

    class Config:
        orm_mode = True

# Dependencia para la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoints
@router.get("/profesores", response_model=list[Profesor])
async def get_profesores(db: Session = Depends(get_db)):
    return db.query(Profesores).all()

@router.get("/profesores/{id}", response_model=Profesor)
async def get_profesor(id: int, db: Session = Depends(get_db)):
    profesor = db.query(Profesores).filter(Profesores.id == id).first()
    if not profesor:
        raise HTTPException(status_code=404, detail="Profesor no encontrado")
    return profesor

@router.post("/profesores", response_model=Profesor, status_code=201)
async def create_profesor(profesor: Profesor, db: Session = Depends(get_db)):
    db_profesor = Profesores(**profesor.dict())
    try:
        db.add(db_profesor)
        db.commit()
        db.refresh(db_profesor)
        return db_profesor
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al guardar el profesor: " + str(e))

@router.put("/profesores/{id}", response_model=Profesor)
async def update_profesor(id: int, profesor_recibido: Profesor, db: Session = Depends(get_db)):
    profesor = db.query(Profesores).filter(Profesores.id == id).first()
    if not profesor:
        raise HTTPException(status_code=404, detail="Profesor no encontrado")
    for key, value in profesor_recibido.dict().items():
        setattr(profesor, key, value)
    db.commit()
    db.refresh(profesor)
    return profesor

@router.delete("/profesores/{id}", response_model=dict)
async def delete_profesor(id: int, db: Session = Depends(get_db)):
    profesor = db.query(Profesores).filter(Profesores.id == id).first()
    if not profesor:
        raise HTTPException(status_code=404, detail="Profesor no encontrado")
    db.delete(profesor)
    db.commit()
    return {"message": "Profesor eliminado"}

