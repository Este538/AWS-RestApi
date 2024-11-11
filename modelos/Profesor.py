from pydantic import BaseModel, Field, ValidationError, root_validator
from typing import Optional

class Profesor(BaseModel):
    id: int = Field(...,gt=0, strict=True)
    numeroEmpleado: int = Field(...,strict=True, gt=0,le=999999)
    nombres: str = Field(...,min_length=1,strict=True)
    apellidos: str = Field(...,min_length=1,strict=True)
    horasClase: int = Field(...,gt=0,le=49,strict=True)

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
        