from pydantic import BaseModel

class PartidaDTO(BaseModel):
    usuario: str
    clave: str
    posicion: dict
    numeroEscena: int
    anguloVision: float
    saltosMaximos: int
    numeroBotonActual: int
    estaConectado: bool
    token: str