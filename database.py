from motor.motor_asyncio import AsyncIOMotorClient
from decouple import config

MONGODB_URL = config("MONGODB_URL", default="mongodb://localhost:27017")
DATABASE_NAME = config("DATABASE_NAME", default="adso_db")

client = AsyncIOMotorClient(MONGODB_URL)

database = client[DATABASE_NAME]

coleccion_entradas = database["entradas_eventos"]

async def verificar_conexion():
    """Función de comprobación de estado de la conexión al iniciar la API"""
    try:
        await client.admin.command('ping')
        print(f" Conexión exitosa a MongoDB - Base de Datos: '{DATABASE_NAME}'")
    except Exception as e:
        print(f" Error de conexión a MongoDB: {e}")
