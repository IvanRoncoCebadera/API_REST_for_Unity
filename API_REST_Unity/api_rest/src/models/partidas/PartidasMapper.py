from models.partidas.Partida import Partida
from models.partidas.PartidaDTO import PartidaDTO

def toPartidaDTO(partida: Partida) -> PartidaDTO:
    return PartidaDTO(
        usuario = partida.usuario,
        clave = partida.clave,
        posicion = partida.posicion.model_dump(),
        numeroEscena = partida.numeroEscena,
        anguloVision = partida.anguloVision,
        saltosMaximos = partida.saltosMaximos,
        numeroBotonActual = partida.numeroBotonActual,
        estaConectado= partida.estaConectado,
        token = partida.token
    )