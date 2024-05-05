from typing import List, Optional
from IRepository.partidas.IPartidaRepo import IPartidaRepo
from models.partidas.PartidaDTO import PartidaDTO
from IRepository import mongo_db

validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["usuario", "clave", "posicion", "numeroEscena", "anguloVision", "saltosMaximos", "numeroBotonActual", "estaConectado", "token"],
        "properties": {
            "usuario": { "bsonType": "string", "description": "Nombre del usuario al que pertenece el guardado" },
            "clave": { "bsonType": "string", "description": "Contraseña encryptada para el inicio de sesión" },
            "posicion": {
                "bsonType": "object",
                "required": ["x", "y", "z"],
                "properties": {
                    "x": { "bsonType": "number", "description": "Componente X del vector de posición" },
                    "y": { "bsonType": "number", "description": "Componente Y del vector de posición" },
                    "z": { "bsonType": "number", "description": "Componente Z del vector de posición" }
                }
            },
            "numeroEscena": { "bsonType": "int", "description": "Número de la escena actual del jugador" },
            "anguloVision": { "bsonType": "number", "description": "Ángulo de visión del jugador" },
            "saltosMaximos": { "bsonType": "int", "description": "Número máximo de saltos permitidos para el jugador" },
            "numeroBotonActual": { "bsonType": "int", "description": "Número del botón actual presionado por el jugador" },
            "estaConectado": { "bsonType": "boolean", "description": "Booleano que permite saber si hay alguién usando la cuenta" },
            "token": { "bsonType": "string", "description": "Token único de validación para el usuario" }
        }
    }
}

class PartidaRepoMongo(IPartidaRepo):

    def __init__(self):
        self.db = mongo_db.testdb

        try: 
            self.db.create_collection("lista_partidas", validator = validator)
        except: pass

    def find_all(self) -> List[PartidaDTO]:
        try: return list(self.db.lista_partidas.find())
        except: return []

    def find_by_user(self, usuario: str) -> Optional[PartidaDTO]:
        try: return PartidaDTO(**self.db.lista_partidas.find_one({"usuario": usuario}))
        except: return None

    def add(self, partida: PartidaDTO) -> bool:
        try: self.db.lista_partidas.insert_one(partida.__dict__)
        except Exception as e: 
            print(e)
            return False
        else: return True
    
    def update(self, partida: PartidaDTO) -> bool:
        partida_dict = partida.__dict__
        del partida_dict['clave']
        try: self.db.lista_partidas.update_one({"usuario":partida.usuario}, {"$set":partida_dict})
        except: return False
        else: return True

    def update_connected_status(self, usuario: str, estaConectado: bool) -> bool:
        try: self.db.lista_partidas.update_one({"usuario":usuario}, {"$set": {"estaConectado":estaConectado}}) #Si esto es false, le quito el TOKEN???
        except: return False
        else: return True

    def update_token_content(self, usuario: str, newToken: str) -> bool:
        print("Voy a actulizar el token!!")
        try: self.db.lista_partidas.update_one({"usuario":usuario}, {"$set": {"token":newToken}})
        except: return False
        else: return True

    def delete_by_user(self, usuario: str) -> bool:
        try: self.db.lista_partidas.delete_one({"usuario":usuario})
        except: return False
        else: return True

    def delete_all(self) -> bool:
        try: self.db.lista_partidas.delete_many({})
        except: return False
        else: return True