from fastapi import FastAPI
from mongo_rest.router.RouterMongo import mongo_router
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_ROUTE = "/mongo/partidas"

app = FastAPI()

app.include_router(mongo_router, prefix=MONGO_ROUTE, tags=["MongoDB"])

@app.get("/")
def loadRoutes():
    routes = {"mongo_db": MONGO_ROUTE}
    return routes

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=str(os.getenv("API_URL")), port=int(os.getenv("API_PORT")))
