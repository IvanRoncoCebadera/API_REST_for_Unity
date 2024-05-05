from pydantic import BaseModel
from models.partidas.Vector3 import Vector3

class Partida(BaseModel):
    usuario: str
    clave: str
    posicion: Vector3
    numeroEscena: int
    anguloVision: float
    saltosMaximos: int
    numeroBotonActual: int
    estaConectado: bool