# API REST for Unity

Este proyecto es una API RESTful desarrollada con Python y FastAPI, diseñada para integrarse con el videojuego "La Familia DaVinci", desarrollado en Unity. La API utiliza JWT y MD5 para la seguridad, almacena datos en una base de datos MongoDB y se despliega utilizando Docker Compose, siendo empaquetado y levantado en un Portaniner.

El objetivo de la API es sencillo. Permitir la conexión del usuario con un servicio en línea que le permita guardar su partida. A vista del usuario, este podrá crearse una cuenta o iniciar sesión.

## Características

- **Framework**: FastAPI y Uvicorn
- **Seguridad**: JWT (JSON Web Tokens) y MD5
- **Base de Datos**: MongoDB
- **Despliegue**: Docker Compose y Portainer

## Requisitos

- Python 3.7+
- Docker
- Docker Compose

## Instalación

1. Clona el repositorio:
    ```bash
    git clone https://github.com/IvanRoncoCebadera/API_REST_for_Unity.git
    cd API_REST_for_Unity
    ```

2. Crea un entorno virtual y activa el entorno:
    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows usa `venv\Scripts\activate`
    ```

3. Instala las dependencias:
    ```bash
    pip install -r requirements.txt
    ```

## Uso

1. Configura las variables de entorno necesarias en los archivos `.env` dentro del proyecto:
    ```plaintext
    MONGO_URI=mongodb://localhost:27017
    SECRET_KEY=tu_secreto_para_jwt
    ```

2. Inicia la aplicación utilizando Docker Compose:
    ```bash
    docker-compose up --build
    ```

3. La API estará disponible en `http://0.0.0.0:8000` (por defecto).

## Endpoints Principales

- `GET /conexion/`: Verifica si hay conexión.
- `GET /guardados/`: Obtiene una lista de todas las partidas guardadas.
- `GET /guardados/${usuario}&{token}`: Obtiene una partida específica por ID de usuario y token.
- `POST /guardados/`: Guarda una nueva partida.
- `PUT /guardados/${token}`: Actualiza una partida existente verificando el token.
- `PUT /guardados/estadoConexion/${usuario}&{estaConectado}`: Actualiza el estado de conexión de un usuario.
- `DELETE /guardados/${usuario}`: Elimina un juego específico por ID de usuario.
- `DELETE /guardados/`: Elimina todos los juegos guardados.
- `GET /guardados/login/${usuario}&{clave}`: Autentica un usuario y devuelve un token JWT.

## Seguridad

- **JWT**: Utilizado para autenticar y autorizar solicitudes.
- **MD5**: Utilizado para hashear contraseñas antes de almacenarlas en la base de datos.

## Tests

La API cuenta con un fichero de tests que se puede ejecutar tal y como se comenta en el propio fichero. EL fichero de tests comprueba las conexiones através de los Endpoints principales de la aplicación, verificando que todas las funcionalidades esten correctas y comprobando que se establece conexión con la base de datos.

## Base de Datos

El proyecto utiliza MongoDB para almacenar datos. Asegúrate de tener una instancia de MongoDB en funcionamiento y configura la URI de conexión en el archivo `.env`. En el Docker Compose del proyecto, ya viene la configuración para crear una instancia de una MongoDB.

## Despliegue

Para desplegar la aplicación en un entorno de producción, asegúrate de configurar correctamente las variables de entorno y utiliza `docker-compose` para gestionar los contenedores. Adicionalmente, para presentar el proyecto al completo, se desplegó esta API junto la base de datos en un Portainer, el cual se encargo del empaquetado y del despliegue.

## Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue o crea un pull request para discutir cualquier cambio importante antes de realizarlo.

## Licencia

Este proyecto está licenciado bajo la [MIT License](LICENSE).

---

Desarrollado por [Iván Ronco Cebadera](https://github.com/IvanRoncoCebadera)
