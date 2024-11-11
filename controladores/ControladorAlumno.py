from fastapi import APIRouter, HTTPException, Request, FastAPI
from modelos.Alumno import Alumno
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import ValidationError

#Permite trabajar en una clase que no sea la main u app (las ejecutables)
router = APIRouter()

#Por cuestiones de practicidad, se emplea un arreglo
alumnos = []

# Endpoints para Alumnos
@router.get("/alumnos")
async def get_alumnos():
    return alumnos

@router.get("/alumnos/{id}", status_code=200) 
async def get_alumno(id: int):
    for alumno in alumnos:
        if alumno.id == id:
            return alumno
    raise HTTPException(status_code=404, detail="Alumno no encontrado")

@router.post("/alumnos", response_model=Alumno, status_code=201)
async def crear_alumno(alumno: dict):  # Si se recibe como objeto, error 422
    try:
        # Valida el objeto usando Pydantic
        alumno_obj = Alumno(**alumno)  # Aquí se validan los campos explícitamente
        alumnos.append(alumno_obj)
        return alumno_obj
    except ValidationError as e:
        # Devuelve un código 400 si hay un error de validación
        raise HTTPException(status_code=400, detail=e.errors())

@router.put("/alumnos/{id}", response_model=Alumno, status_code=200)
async def subir_alumno(id: int, alumno_recibido: dict):  # Si se recibe como objeto, error 422
    try:
        # Valida el objeto usando Pydantic, de no hacerse así, te ingresa datos erróneos como -20235 
        alumno_obj = Alumno(**alumno_recibido)
    except ValidationError as e:
        # Devuelve un código 400 si hay error de validación
        raise HTTPException(status_code=400, detail=e.errors())

    for index, alumno in enumerate(alumnos):
        if alumno.id == id:
            alumnos[index] = alumno_obj
            return jsonable_encoder(alumno_obj)

    raise HTTPException(status_code=400, detail="Alumno no encontrado")

@router.delete("/alumnos/{id}", status_code=200) 
async def eliminar_alumno(id: int):
    for index, alumno in enumerate(alumnos):
        if alumno.id == id:
            del alumnos[index]
            return {"message": "Alumno eliminado"}
    raise HTTPException(status_code=404, detail="Alumno no encontrado")
