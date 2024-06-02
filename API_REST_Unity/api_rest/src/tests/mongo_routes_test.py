from datetime import datetime, timedelta
import hashlib
import jwt
import pytest
from fastapi.testclient import TestClient

from ..mongo_rest.repository.partidas.PartidaRepoMongo import PartidaRepoMongo
from ..app import app

# Para ejecutar las pruebas, hacerlo en local. Levantar la base de datos de MongoDB.
# Instalar Pytest: 'pip install pytest'
# Situarse en el directorio raiz del proyecto y ejecutar: 'pytest'

partidas_repo = PartidaRepoMongo()

client = TestClient(app)

MONGO_ROUTE = "/mongo/partidas"

SECRET_KEY = 'DaVinci'

def generate_token(user_id, expiration_seconds=0):
    expiration = datetime.utcnow() + timedelta(seconds=expiration_seconds)
    payload = {'user_id': user_id, 'exp': expiration}
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

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

# Datos de prueba
usuario_test = "testuser"
usuario_no_existente = "USUARIO_FALSO"
clave_test = "testpassword"
clave_invalida = "CLAVE_INVALIDA"
partida_test = {
    "usuario": usuario_test,
    "clave": clave_test,
    "posicion": {
      "x": -820.0,
      "y": 20.0,
      "z": -1320.0
    },
    "numeroEscena": 6,
    "anguloVision": 270.0,
    "saltosMaximos": 1,
    "numeroBotonActual": 0,
    "estaConectado": True,
    "token": ""
  }

# Limpiar datos de prueba
def cleanup_test_data():
    partidas_repo.delete_by_user(usuario_test)

# Fixtures para limpiar después de cada prueba
@pytest.fixture(scope="module", autouse=True)
def setup_and_teardown():
    yield
    cleanup_test_data()

############################################ ROUTES ##############################################

def test_get_all_routes():
    response = client.get("/")
    assert response.status_code == 200
    jsonResponse = {'mongo_db': '/mongo/partidas'}
    assert response.json() == jsonResponse

def test_get_all_routes_from_router():
    response = client.get("/mongo/partidas")
    assert response.status_code == 200
    jsonResponse = {
          "DO_I_HAVE_CONNECTION": "/conexion/",
          "GET_ALL_GAMES_ROUTE": "/guardados/",
          "GET_GAME_BY_ID_ROUTE": "/guardados/${usuario}&{token}",
          "POST_GAME_ROUTE": "/guardados/",
          "PUT_GAME_ROUTE": "/guardados/${token}",
          "UPDATE_CONNECTED_STATUS": "/guardados/estadoConexion/${usuario}&{estaConectado}",
          "DELETE_GAME_BY_ID_ROUTE": "/guardados/${usuario}",
          "DELETE_ALL_GAMES_ROUTE": "/guardados/",
          "LOG_IN": "/guardados/login/${usuario}&{clave}"
        }
    assert response.json() == jsonResponse

############################################ CONNECTION ##############################################

def test_check_if_i_have_connection():
    response = client.get(MONGO_ROUTE+"/conexion/")
    assert response.status_code == 200
    assert response.json() is True

############################################ ADD ##############################################

def test_add_game():
    cleanup_test_data()
    response = client.post(MONGO_ROUTE+"/guardados/", json=partida_test)
    assert response.status_code == 200
    assert "token" in response.json()
    token = response.json()["token"]

    # Guardar el token para pruebas posteriores
    partida_test["token"] = token
    partida_test["clave"] = encrypt_password(clave_test)

def test_add_already_existing_game():
    response = client.post(MONGO_ROUTE+"/guardados/", json=partida_test)
    assert response.status_code == 406
    jsonResponse = {
        "detail": "No se guardo la partida"
    }
    assert response.json() == jsonResponse

############################################ PUT ##############################################

# Primero hacer lo del update, para crear poner un token que expire tras 0 segundos o algo así, justo antes del tests del token expiro en las distintas funciones

def test_update_game():
    assert "token" in partida_test, "Token no encontrado. Ejecuta test_add_game primero."
    previous_token = partida_test["token"]
    partida_test["token"] = generate_token(partida_test["usuario"], 60)
    response = client.put(f"{MONGO_ROUTE}/guardados/${previous_token}", json=partida_test)
    assert response.status_code == 200
    jsonResponse = {
        "message": "La partida se actualizo exitosamente"
    }
    assert response.json() == jsonResponse

#¡ESTO NO ES UN TEST!
def update_to_expirate_token():
    partida_test["token"] = generate_token(usuario_test, 0)
    partidas_repo.update_token_content(usuario_test, partida_test["token"])

#¡ESTO NO ES UN TEST!
def update_connected_status(newStatus: bool):
    return partidas_repo.update_connected_status(usuario_test, newStatus)

#¡ESTO NO ES UN TEST!
def update_to_available_token():
    if update_connected_status(False):
        response = client.get(f"{MONGO_ROUTE}/guardados/login/${usuario_test}&{clave_test}")
        partida_test["token"] = response.json()
        update_connected_status(True)

def test_update_game_but_token_expired():
    assert "token" in partida_test, "Token no encontrado. Ejecuta test_add_game primero."

    update_to_expirate_token()

    previous_token = partida_test["token"]
    response = client.put(f"{MONGO_ROUTE}/guardados/${previous_token}", json=partida_test)
    assert response.status_code == 401
    jsonResponse = {
        "detail": "El token expiro"
    }
    assert response.json() == jsonResponse

    #Ahora, para los siguientes tests, vuelvo a poner un token válido:
    update_to_available_token()

############################################ PUT CONNECTED STATUS ##############################################

def test_update_connected_status():
    # Ponerlo a False de nuevo
    response = client.put(f"{MONGO_ROUTE}/guardados/estadoConexion/${usuario_test}&False")
    assert response.status_code == 200
    jsonResponse = {"message": "Se actualizo el estado de la conexión a: False"}
    assert response.json() == jsonResponse

    # Ponerlo a True de nuevo
    response = client.put(f"{MONGO_ROUTE}/guardados/estadoConexion/${usuario_test}&True")
    assert response.status_code == 200
    jsonResponse = {"message": "Se actualizo el estado de la conexión a: True"}
    assert response.json() == jsonResponse

def test_update_connected_status_but_not_found():
    response = client.put(f"{MONGO_ROUTE}/guardados/estadoConexion/${usuario_no_existente}&False")
    assert response.status_code == 406
    jsonResponse = {"detail": "No se actualizo el estado de la conexión"}
    assert response.json() == jsonResponse

############################################ GET ##############################################

def test_get_all_games():
    response = client.get(MONGO_ROUTE+"/guardados/")
    assert response.status_code == 200

    token = partida_test["token"] #Guardo el valor del token
    partida_test["token"] = ""

    clave = partida_test["clave"] #Guardo el valor de la clave
    partida_test["clave"] = ""

    assert response.json()[-1] == partida_test #Comparo habiendo quitado la clave y el token

    partida_test["token"] = token #Devuelvo los valores para el resto de pruebas!!
    partida_test["clave"] = clave

def test_get_game_by_user():
    assert "token" in partida_test, "Token no encontrado. Ejecuta test_add_game primero."
    token = partida_test["token"]
    response = client.get(f"{MONGO_ROUTE}/guardados/${usuario_test}&{token}")
    assert response.status_code == 200
    partida = response.json()
    assert partida["usuario"] == usuario_test

def test_get_game_by_user_but_not_found():
    assert "token" in partida_test, "Token no encontrado. Ejecuta test_add_game primero."
    token = partida_test["token"]
    response = client.get(f"{MONGO_ROUTE}/guardados/${usuario_no_existente}&{token}")
    assert response.status_code == 404
    jsonResponse = {
        "detail": "Partida no encontrada"
    }
    assert response.json() == jsonResponse

def test_get_game_by_user_but_token_invalid():
    assert "token" in partida_test, "Token no encontrado. Ejecuta test_add_game primero."
    response = client.get(f"{MONGO_ROUTE}/guardados/${usuario_test}&TOKEN_INVALIDO")
    assert response.status_code == 404
    jsonResponse = {
        "detail": "Token no válido"
    }
    assert response.json() == jsonResponse

def test_get_game_by_user_but_token_expired():
    assert "token" in partida_test, "Token no encontrado. Ejecuta test_add_game primero."

    update_to_expirate_token()

    token = partida_test["token"]
    response = client.get(f"{MONGO_ROUTE}/guardados/${usuario_test}&{token}")
    assert response.status_code == 401
    jsonResponse = {
        "detail": "El token expiro"
    }
    assert response.json() == jsonResponse

    #Ahora, para los siguientes tests, vuelvo a poner un token válido:
    update_to_available_token()

############################################ LOGIN ##############################################

def test_log_in():
    update_connected_status(False)

    response = client.get(f"{MONGO_ROUTE}/guardados/login/${usuario_test}&{clave_test}")
    assert response.status_code == 200
    token = response.json()
    assert isinstance(token, str)
    assert len(token) > 0

def test_log_in_but_user_not_found():
    response = client.get(f"{MONGO_ROUTE}/guardados/login/${usuario_no_existente}&{clave_test}")
    assert response.status_code == 200
    assert response.json() == '3'

def test_log_in_but_user_password_invalid():
    response = client.get(f"{MONGO_ROUTE}/guardados/login/${usuario_test}&{clave_invalida}")
    assert response.status_code == 200
    assert response.json() == '2'

def test_log_in_but_user_but_someone_is_already_connected():
    update_connected_status(True)

    response = client.get(f"{MONGO_ROUTE}/guardados/login/${usuario_test}&{clave_test}")
    assert response.status_code == 200
    assert response.json() == '1'

############################################ DELETE ##############################################

def test_delete_game_by_user():
    response = client.delete(f"{MONGO_ROUTE}/guardados/${usuario_test}")
    assert response.status_code == 200
    jsonResponse = {"message": "Partida del usuario ("+usuario_test+") borrada exitosamente"}
    assert response.json() == jsonResponse

def test_delete_all_games():
    response = client.delete(MONGO_ROUTE+"/guardados/")
    assert response.status_code == 200
    jsonResponse = {"message": "Se han borrado todas las partidas"}
    assert response.json() == jsonResponse