from contextlib import asynccontextmanager
from fastapi import FastAPI
from middleware import apply_cors_middleware
from absolute_url import get_absolute_url
from db.db_connection import MongoDBConnection


@asynccontextmanager
async def lifespan(app: FastAPI):
    mongo_connection = MongoDBConnection(db_name="leoDB")
    app.db = await mongo_connection.db_connection()
    app.db_uri = await mongo_connection.db_uri()
    
    yield
    
    # release the resources
    await mongo_connection.close()


app = FastAPI(lifespan=lifespan)
app = apply_cors_middleware(app)  # Middlewares...
app = get_absolute_url(app=app)  # Routes

# App root
@app.get('/', tags=['Root'])
async def root():
    return {'message': 'Welcome to this fantastic LeoChat app! Just enjoy this app...!'}