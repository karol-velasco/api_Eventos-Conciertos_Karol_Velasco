from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Annotated
from bson import ObjectId
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema


class _ObjectIdPydanticAnnotation:

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        def validate(v):
            if isinstance(v, ObjectId):
                return str(v)
            if isinstance(v, str) and ObjectId.is_valid(v):
                return v
            raise ValueError("ID inválido de MongoDB (ObjectId)")

        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.no_info_plain_validator_function(validate),
            serialization=core_schema.to_string_ser_schema(),
        )

PyObjectId = Annotated[str, _ObjectIdPydanticAnnotation]

class EntradaConciertoBase(BaseModel):
    evento: str = Field(
        ...,
        min_length=3,
        max_length=150,
        description="Nombre del evento o concierto",
        example="Concierto Tour Mundial 2026",
    )
    zona_asiento: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Ubicación, localidad o número de asiento asignado",
        example="VIP Occidental - Fila A Asiento 12",
    )
    precio_entrada: float = Field(
        ...,
        gt=0,
        description="Valor o precio de la entrada",
        example=250000.0,
    )
    pagada: bool = Field(
        default=False,
        description="Estado de pago de la entrada",
    )


class EntradaConciertoCreate(EntradaConciertoBase):
    pass

class EntradaConciertoUpdate(BaseModel):
    evento: Optional[str] = Field(None, min_length=3, max_length=150)
    zona_asiento: Optional[str] = Field(None, min_length=2, max_length=100)
    precio_entrada: Optional[float] = Field(None, gt=0)
    pagada: Optional[bool] = None


class EntradaConcierto(EntradaConciertoBase):
    id: PyObjectId = Field(alias="_id", description="Identificador único ObjectId de MongoDB")

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "_id": "654321789abcdef012345678",
                "evento": "Concierto Tour Mundial 2026",
                "zona_asiento": "VIP Occidental - Fila A Asiento 12",
                "precio_entrada": 250000.0,
                "pagada": True,
            }
        },
    )
