import uuid

from pydantic import BaseModel


class RegionResponse(BaseModel):
    id: uuid.UUID
    name: str
    type: str  # 'LOCAL' (viloyat) or 'ABROAD' (xorijiy davlat)


class RegionListResponse(BaseModel):
    items: list[RegionResponse]


class ReceptionPlaceResponse(BaseModel):
    id: uuid.UUID
    name: str


class ReceptionPlaceListResponse(BaseModel):
    items: list[ReceptionPlaceResponse]


class AppealTypeResponse(BaseModel):
    id: uuid.UUID
    name: str


class AppealTypeListResponse(BaseModel):
    items: list[AppealTypeResponse]
