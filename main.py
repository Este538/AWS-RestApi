import uvicorn
from fastapi import FastAPI, Request
from controladores.ControladorAlumno import router as ControladorAlumno
from controladores.ControladorProfesor import router as ControladorProfesor
from fastapi.responses import JSONResponse
from pydantic import ValidationError

app = FastAPI()


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    # Aquí puedes personalizar la respuesta para devolver un código 400 en lugar de 422
    return JSONResponse(
        status_code=400,
        content={"detail": exc.errors()},
    )

app.include_router(ControladorAlumno)
app.include_router(ControladorProfesor)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
