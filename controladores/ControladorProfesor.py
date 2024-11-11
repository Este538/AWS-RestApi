from fastapi import APIRouter, HTTPException
from pydantic import ValidationError
from modelos.Profesor import Profesor

#Permite crear rutas fuera del main
router = APIRouter()

# Cuestiones de práctica, un arreglo
profesores = []

# Endpoints para Profesores
@router.get("/profesores")
def get_profesores():
    return profesores

@router.get("/profesores/{id}", status_code=200)
def get_profesor(id: int):
    for profesor in profesores:
        if profesor.id == id:
            return profesor
    raise HTTPException(status_code=404, detail="Profesor no encontrado")

@router.post("/profesores", response_model=Profesor, status_code=201)
def create_profesor(profesor: dict):  # Si recibe sin ser diccionario, error 422
    try:
        # Validación manual usando Pydantic, si no es así, los datos entran sin restricción
        profesor_obj = Profesor(**profesor)
        profesores.append(profesor_obj)
        return profesor_obj
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.errors())  

@router.put("/profesores/{id}", response_model=Profesor, status_code=200)
def update_profesor(id: int, updated_profesor: dict):  # Recibe un diccionario para validación manual
    try:
        # Validación manual usando Pydantic
        profesor_obj = Profesor(**updated_profesor)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.errors())  # Error 400 en lugar de 422

    for index, profesor in enumerate(profesores):
        if profesor.id == id:
            profesores[index] = profesor_obj
            return profesor_obj

    raise HTTPException(status_code=404, detail="Profesor no encontrado")

@router.delete("/profesores/{id}", status_code=200)
def delete_profesor(id: int):
    for index, profesor in enumerate(profesores):
        if profesor.id == id:
            del profesores[index]
            return {"message": "Profesor eliminado"}
    raise HTTPException(status_code=404, detail="Profesor no encontrado")

