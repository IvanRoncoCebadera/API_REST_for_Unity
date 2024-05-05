from typing import TypeVar, Generic, List, Optional

T = TypeVar('T')
ID = TypeVar('ID')

class IRepository(Generic[T, ID]):
    def find_all(self) -> List[T]:
        raise NotImplementedError("Método abstracto")

    def find_by_id(self, id: ID) -> Optional[T]:
        raise NotImplementedError("Método abstracto")

    def add(self, entity: T) -> bool:
        raise NotImplementedError("Método abstracto")
    
    def update(self, entity: T) -> bool:
        raise NotImplementedError("Método abstracto")

    def delete_by_id(self, id: ID) -> bool:
        raise NotImplementedError("Método abstracto")

    def delete_all(self,) -> bool:
        raise NotImplementedError("Método abstracto")
