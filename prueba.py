from modelos.Alumno import Alumno
from modelos.Profesor import Profesor
from pydantic import ValidationError

try:
    profesor1 = Profesor(id=1, numeroEmpleado=12359, nombres="Juan", apellidos="Gonzalez", horasClase=10)
    print(profesor1)
except ValidationError as e:
    print("Error de validación en profesor1:", e)

try:
    profesor_invalido = Profesor(id=1.5, numeroEmpleado=12359.5, nombres="Juan", apellidos="Gonzalez", horasClase=10)
    print(profesor_invalido)
except ValidationError as e:
    print("Error de validación en profesor_invalido:", e)

try:
    alumno1 = Alumno(id=1,nombres="Juan", apellidos="Gonzalez", matricula="A202467",promedio=15.6)
    print(alumno1)
except ValidationError as e:
    print("Error de validación en profesor1:", e)

try:
    alumno_invalido = Alumno(id=1,nombres="Juan", apellidos="Gonzalez", matricula=202467,promedio=15.6)
    print(alumno_invalido)
except ValidationError as e:
    print("Error de validación en profesor_invalido:", e)

