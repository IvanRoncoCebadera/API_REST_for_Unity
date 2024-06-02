FROM python:alpine3.19

WORKDIR /usr/src/app

COPY requirements.txt ./
COPY src/.env ./

RUN pip install --no-cache-dir -r requirements.txt

# Copiar todos los archivos y carpetas de src al contenedor
COPY src .

# Eliminar la carpeta tests dentro del contenedor
RUN rm -rf ./tests

CMD [ "python", "./app.py" ]