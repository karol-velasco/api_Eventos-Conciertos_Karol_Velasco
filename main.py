from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from bson import ObjectId

from models import EntradaConcierto, EntradaConciertoCreate, EntradaConciertoUpdate
from database import coleccion_entradas, verificar_conexion

app = FastAPI(
    title="API Eventos y Conciertos - SENA ADSO",
    description="API RESTful asíncrona con FastAPI y MongoDB (FARM Stack).",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_db_client():
    await verificar_conexion()

@app.get("/", tags=["Raíz"])
async def root():
    return {
        "mensaje": "Bienvenido a la API de Eventos y Conciertos Asíncrona con MongoDB (SENA ADSO)",
        "documentacion": "/docs"
    }


@app.post(
    "/entradas",
    response_model=EntradaConcierto,
    status_code=status.HTTP_201_CREATED,
    tags=["Entradas"],
    summary="Registrar una nueva entrada en MongoDB"
)
async def create_entrada(entrada_in: EntradaConciertoCreate):
    entrada_existente = await coleccion_entradas.find_one({
        "evento": entrada_in.evento,
        "zona_asiento": entrada_in.zona_asiento
    })
    if entrada_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe una entrada registrada para '{entrada_in.evento}' en '{entrada_in.zona_asiento}'."
        )

    nueva_entrada = entrada_in.model_dump()

    resultado = await coleccion_entradas.insert_one(nueva_entrada)

    entrada_creada = await coleccion_entradas.find_one({"_id": resultado.inserted_id})
    return entrada_creada


@app.get(
    "/entradas",
    response_model=List[EntradaConcierto],
    status_code=status.HTTP_200_OK,
    tags=["Entradas"],
    summary="Listar todas las entradas"
)
async def get_entradas():
    entradas = []
    cursor = coleccion_entradas.find()
    async for documento in cursor:
        entradas.append(documento)
    return entradas


@app.get(
    "/entradas/{id}",
    response_model=EntradaConcierto,
    status_code=status.HTTP_200_OK,
    tags=["Entradas"],
    summary="Buscar entrada por ObjectId"
)
async def get_entrada_por_id(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El formato del ID '{id}' no es un ObjectId válido de MongoDB."
        )

    entrada = await coleccion_entradas.find_one({"_id": ObjectId(id)})
    if entrada:
        return entrada

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"La entrada con ID '{id}' no fue encontrada en la base de datos."
    )

@app.put(
    "/entradas/{id}",
    response_model=EntradaConcierto,
    status_code=status.HTTP_200_OK,
    tags=["Entradas"],
    summary="Actualizar estado o campos de una entrada"
)
async def update_entrada(id: str, entrada_update: EntradaConciertoUpdate):
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El formato del ID '{id}' no es un ObjectId válido."
        )

    datos_a_actualizar = entrada_update.model_dump(exclude_unset=True)

    if len(datos_a_actualizar) >= 1:
        resultado_actualizacion = await coleccion_entradas.update_one(
            {"_id": ObjectId(id)},
            {"$set": datos_a_actualizar}
        )

        if resultado_actualizacion.modified_count == 1 or resultado_actualizacion.matched_count == 1:
            entrada_modificada = await coleccion_entradas.find_one({"_id": ObjectId(id)})
            return entrada_modificada

    entrada_existente = await coleccion_entradas.find_one({"_id": ObjectId(id)})
    if entrada_existente:
        return entrada_existente

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"No es posible actualizar. La entrada con ID '{id}' no existe."
    )


@app.delete(
    "/entradas/{id}",
    status_code=status.HTTP_200_OK,
    tags=["Entradas"],
    summary="Eliminar entrada de MongoDB"
)
async def delete_entrada(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El formato del ID '{id}' no es un ObjectId válido."
        )

    resultado_eliminacion = await coleccion_entradas.delete_one({"_id": ObjectId(id)})

    if resultado_eliminacion.deleted_count == 1:
        return {"mensaje": f"Entrada con ID '{id}' eliminada exitosamente de MongoDB."}

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"No es posible eliminar. La entrada con ID '{id}' no existe en la base de datos."
    )
