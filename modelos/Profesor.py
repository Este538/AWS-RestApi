from pydantic import BaseModel, Field, ValidationError, root_validator, validator
from typing import Optional

class Profesor(BaseModel):
    id: int = Field(...,ge=0)
    numeroEmpleado: int = Field(..., ge=0)
    nombres: str = Field(...,min_length=1)
    apellidos: str = Field(...,min_length=1)
    horasClase: int = Field(...,ge=0)

    @root_validator(pre=True)
    def check_strict_integers(cls, values):
        # Validar que los campos id, numeroEmpleado, y horasClase sean estrictamente enteros
        for field in ['id', 'numeroEmpleado', 'horasClase']:
            if not isinstance(values.get(field), int):
                raise TypeError(f"El campo {field} debe ser un entero estricto.")
        return values
    
    @root_validator(pre=True)
    def check_not_null(cls, values):
        # Verificar que ninguno de los campos necesarios sea None (null en JS)
        for field in ['id', 'numeroEmpleado', 'nombres', 'apellidos', 'horasClase']:
            if values.get(field) is None:
                raise ValueError(f"El campo '{field}' no puede ser nulo (None).")
        return values
    
    # Validador para asegurar que los campos 'nombres' y 'apellidos' no sean cadenas vacías
    @validator('nombres', 'apellidos')
    def check_not_empty(cls, v, field):
        if not v.strip():  # .strip() elimina espacios al principio y final
            raise ValueError(f"El campo '{field.name}' no puede ser vacío.")
        return v
        