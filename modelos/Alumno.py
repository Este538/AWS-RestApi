from pydantic import BaseModel, Field, validator, root_validator, ValidationError
from typing import Optional
import re

matricula_expression = r"^A[0-9]\d{0,5}$"

class Alumno(BaseModel):
    id: int = Field(..., ge=0)
    nombres: str = Field(..., min_length=1)
    apellidos: str = Field(..., min_length=1)
    matricula: str = Field(..., regex=matricula_expression)
    promedio: float = Field(..., ge=0, lt=99.99)

    # Validador para la matrícula
    @validator('matricula')
    def validate_matricula(cls, v):
        if not re.match(matricula_expression, v):
            raise ValueError("La matrícula debe comenzar con la letra 'A' seguida de un número positivo.")
        return v
    
    # Validador para asegurar que los campos 'nombres' y 'apellidos' no sean cadenas vacías
    @validator('nombres', 'apellidos')
    def check_not_empty(cls, v, field):
        if not v.strip():  # .strip() elimina espacios al principio y final
            raise ValueError(f"El campo '{field.name}' no puede ser vacío.")
        return v

    # Validador para los valores nulos
    @root_validator(pre=True)
    def check_not_null(cls, values):
        required_fields = ['id', 'nombres', 'apellidos', 'matricula', 'promedio']
        for field in required_fields:
            if values.get(field) is None:
                raise ValueError(f"El campo '{field}' no puede ser nulo.")
        return values

    # Validación adicional para el tipo de 'id' asegurando que sea un número entero
    @root_validator(pre=True)
    def check_strict_integers(cls, values):
        for field in ['id']:
            if not isinstance(values.get(field), int):
                raise TypeError(f"El campo '{field}' debe ser un entero estricto.")
        return values

# Ejemplo de uso
try:
    alumno = Alumno(id=123, nombres="", apellidos="Pérez", matricula=-.46, promedio=85.5)
    print(alumno)
except ValidationError as e:
    print(e)


    


   



