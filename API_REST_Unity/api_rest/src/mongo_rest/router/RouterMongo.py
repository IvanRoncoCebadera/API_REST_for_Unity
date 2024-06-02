from typing  import List
from fastapi import APIRouter, HTTPException
from IRepository.partidas import IPartidaRepo
from mongo_rest.repository.partidas.PartidaRepoMongo import PartidaRepoMongo
from models.partidas.Partida import Partida
from models.partidas.PartidaDTO import PartidaDTO
from models.partidas.PartidasMapper import toPartidaDTO
import hashlib
import jwt
from datetime import datetime, timedelta

SECRET_KEY = 'DaVinci'

partidasRepo: IPartidaRepo = PartidaRepoMongo()

def generate_token(user_id, expiration_days=30):
    expiration = datetime.utcnow() + timedelta(days=expiration_days)
    payload = {'user_id': user_id, 'exp': expiration}
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        # El token ha expirado
        return None
    except jwt.InvalidTokenError:
        # El token no es válido
        return None

mongo_router = APIRouter()

DO_I_HAVE_CONNECTION="/conexion/"
GET_ALL_GAMES_ROUTE="/guardados/"
GET_GAME_BY_ID_ROUTE="/guardados/${usuario}&{token}"
POST_GAME_ROUTE="/guardados/"
PUT_GAME_ROUTE="/guardados/${token}"
UPDATE_CONNECTED_STATUS="/guardados/estadoConexion/${usuario}&{estaConectado}"
DELETE_GAME_BY_ID_ROUTE="/guardados/${usuario}"
DELETE_ALL_GAMES_ROUTE="/guardados/"
LOG_IN="/guardados/login/${usuario}&{clave}"

###############################  Rutas  ###############################

@mongo_router.get("/", tags=["MongoDB"])
async def get_all_routes():
    routes = { 
        "DO_I_HAVE_CONNECTION": DO_I_HAVE_CONNECTION,
        "GET_ALL_GAMES_ROUTE": GET_ALL_GAMES_ROUTE, 
        "GET_GAME_BY_ID_ROUTE": GET_GAME_BY_ID_ROUTE, 
        "POST_GAME_ROUTE": POST_GAME_ROUTE, 
        "PUT_GAME_ROUTE": PUT_GAME_ROUTE,
        "UPDATE_CONNECTED_STATUS": UPDATE_CONNECTED_STATUS,
        "DELETE_GAME_BY_ID_ROUTE": DELETE_GAME_BY_ID_ROUTE, 
        "DELETE_ALL_GAMES_ROUTE": DELETE_ALL_GAMES_ROUTE,
        "LOG_IN": LOG_IN
        }
    return routes

@mongo_router.get(DO_I_HAVE_CONNECTION, response_model=bool, tags=["MongoDB"])
async def check_if_i_have_connection():
    return True

@mongo_router.get(GET_ALL_GAMES_ROUTE, response_model=List[PartidaDTO], tags=["MongoDB"])
async def get_game_files():
    partidas = partidasRepo.find_all()
    for partida in partidas:
        partida['clave'] = ''
        partida['token'] = ''
    return partidas

@mongo_router.get(GET_GAME_BY_ID_ROUTE, response_model=PartidaDTO, tags=["MongoDB"])
async def get_game_by_user(usuario: str, token: str = "NO", doRaise: bool = True):
    partida = partidasRepo.find_by_user(usuario)
    if partida is not None:
        if partida.token == token:
            if verify_token(token):
                if(doRaise):  partida.token = ""
                partida.clave = ""
                return partida
            else:
                if doRaise:
                    raise HTTPException(status_code=401, detail="El token expiro")
                else: return None
        elif token == "NO":
            if(doRaise):  partida.token = ""
            partida.clave = ""
            return partida
        else:
            if doRaise:
                raise HTTPException(status_code=404, detail="Token no válido")
            else: return None
    else:
        if doRaise:
            raise HTTPException(status_code=404, detail="Partida no encontrada")
        else: return None
    
@mongo_router.post(POST_GAME_ROUTE, tags=["MongoDB"])
async def add_game(partida: Partida):
    if await get_game_by_user(partida.usuario, "NO", False) is None:
        password = encrypt_password(partida.clave)
        token = generate_token(partida.usuario)
        partida_encriptada: Partida = Partida(
            usuario=partida.usuario,
            clave=password,
            posicion=partida.posicion,
            numeroEscena=partida.numeroEscena,
            anguloVision=partida.anguloVision,
            saltosMaximos=partida.saltosMaximos,
            numeroBotonActual=partida.numeroBotonActual,
            estaConectado=True,
            token=token
        )
        salioBien = partidasRepo.add(toPartidaDTO(partida_encriptada))
    else:
        salioBien = False
    if salioBien:
        return {"token": token}
    else:
        raise HTTPException(status_code=406, detail="No se guardo la partida") #Partida con un nombre ya existente o fallo de conexión con la BBDD


def encrypt_password(password):
    # Convertir la contraseña en bytes antes de pasarla al algoritmo de hash
    password_bytes = password.encode('utf-8')

    # Crear un objeto hash MD5
    md5_hash = hashlib.md5()

    # Actualizar el objeto hash con la contraseña en bytes
    md5_hash.update(password_bytes)

    # Obtener el hash MD5 como una cadena hexadecimal
    encrypted_password = md5_hash.hexdigest()

    return encrypted_password
    
@mongo_router.put(PUT_GAME_ROUTE, tags=["MongoDB"])
async def update_game(partida: Partida, token: str):
    if verify_token(token):
        if await get_game_by_user(partida.usuario, token, False) is None: salioBien = False
        else:
            if(partida.token == ""): partida.token = token #Añadido que se puede actualizar el token, esto solo se usa para los tests!!!
            salioBien = partidasRepo.update(toPartidaDTO(partida)) #Esta partida, debería tener la password vacia. Si puedo actulizar, es porque ya inicie sesión antes.
        if salioBien:
            return {"message": "La partida se actualizo exitosamente"}
        else:
            raise HTTPException(status_code=406, detail="No se actualizo la partida") #No se ha encontrado al usuario o fallo de conexión con la BBDD
    else:
        raise HTTPException(status_code=401, detail="El token expiro")
    
@mongo_router.put(UPDATE_CONNECTED_STATUS, tags=["MongoDB"])
async def update_connected_status(usuario: str, estaConectado: str):
    if await get_game_by_user(usuario, "NO", False) is None: salioBien = False
    else:
        salioBien = partidasRepo.update_connected_status(usuario, estaConectado.lower() == "true") 
    if salioBien:
        return {"message": "Se actualizo el estado de la conexión a: "+estaConectado}
    else:
        raise HTTPException(status_code=406, detail="No se actualizo el estado de la conexión") #Usuario no encontrado o fallo de conexión con la BBDD

@mongo_router.delete(DELETE_GAME_BY_ID_ROUTE, tags=["MongoDB"])
async def delete_game_by_user(usuario: str):
    salioBien = partidasRepo.delete_by_user(usuario)
    if salioBien:
        return {"message": "Partida del usuario ("+usuario+") borrada exitosamente"}
    else:
        raise HTTPException(status_code=404, detail="No se ha podido borrar la partida del usuario: "+usuario) #Fallo de conexión con la BBDD
    
@mongo_router.delete(DELETE_ALL_GAMES_ROUTE, tags=["MongoDB"])
async def delete_all_games():
    salioBien = partidasRepo.delete_all()
    if salioBien:
        return {"message": "Se han borrado todas las partidas"}
    else:
        raise HTTPException(status_code=404, detail="No se han podido borrar las partidas") #Fallo de conexión con la BBDD

@mongo_router.get(LOG_IN, response_model=str, tags=["MongoDB"])
def log_in(usuario: str, clave: str):
    partida: Partida = partidasRepo.find_by_user(usuario)
    if partida is not None:
        encrypterPassword = encrypt_password(clave)
        if (partida.clave == encrypterPassword): 
            if(not partida.estaConectado):
                #Generar un nuevo token para el usuario y mandarlo!!
                token = generate_token(partida.usuario)

                actualizado = partidasRepo.update_token_content(partida.usuario, token)

                if actualizado:
                    return token  #Nos loggamos, por lo que le envio el nuevo token
                else:
                    return '4' #Fallo de conexión
            else: return '1' #Hay alguien conectado
        else: return '2' #Contraseña invalida
    else: return '3' #Usuario no encontrado
