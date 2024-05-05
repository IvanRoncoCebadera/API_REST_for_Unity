from IRepository.IRepository import IRepository
from models.partidas.PartidaDTO import PartidaDTO

class IPartidaRepo(IRepository[PartidaDTO, str]):
    def update_connected_status(self, usuario: str, estaConectado: bool) -> bool:
        raise NotImplementedError("Método abstracto")