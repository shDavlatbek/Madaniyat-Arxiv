import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query

from src.api.dependencies import get_person_command_handler, get_person_query_handler
from src.api.middleware.auth import get_current_user, require_admin
from src.api.schemas.person import (
    CreatePersonRequest,
    PersonListResponse,
    PersonResponse,
    TenureResponse,
    UpdatePersonRequest,
)
from src.application.person.commands import CreatePersonCommand, DeletePersonCommand, TenureData, UpdatePersonCommand
from src.application.person.handlers import PersonCommandHandler, PersonQueryHandler
from src.application.person.queries import GetPersonQuery, ListActivePersonsOnDateQuery, ListPersonsQuery
from src.domain.person.entity import Person
from src.domain.user.entity import User

router = APIRouter(prefix="/api/persons", tags=["persons"])


def _to_response(person: Person) -> PersonResponse:
    return PersonResponse(
        id=person.id,
        full_name=person.full_name,
        tenures=[
            TenureResponse(
                id=t.id,
                position=t.position,
                start_date=t.start_date,
                end_date=t.end_date,
                created_at=t.created_at,
            )
            for t in person.tenures
        ],
        created_at=person.created_at,
        updated_at=person.updated_at,
    )


@router.get("", response_model=PersonListResponse)
async def list_persons(
    search: str | None = Query(None),
    handler: PersonQueryHandler = Depends(get_person_query_handler),
    _: User = Depends(get_current_user),
):
    persons = await handler.list_persons(ListPersonsQuery(search=search))
    return PersonListResponse(items=[_to_response(p) for p in persons])


@router.get("/active", response_model=PersonListResponse)
async def list_active_persons(
    date: date = Query(...),
    handler: PersonQueryHandler = Depends(get_person_query_handler),
    _: User = Depends(get_current_user),
):
    persons = await handler.list_active_on_date(ListActivePersonsOnDateQuery(date=date))
    return PersonListResponse(items=[_to_response(p) for p in persons])


@router.get("/{person_id}", response_model=PersonResponse)
async def get_person(
    person_id: uuid.UUID,
    handler: PersonQueryHandler = Depends(get_person_query_handler),
    _: User = Depends(get_current_user),
):
    person = await handler.get_person(GetPersonQuery(person_id=person_id))
    return _to_response(person)


@router.post("", response_model=PersonResponse, status_code=201)
async def create_person(
    request: CreatePersonRequest,
    handler: PersonCommandHandler = Depends(get_person_command_handler),
    _: User = Depends(require_admin),
):
    person = await handler.create(CreatePersonCommand(
        full_name=request.full_name,
        tenures=[TenureData(position=t.position, start_date=t.start_date, end_date=t.end_date) for t in request.tenures],
    ))
    return _to_response(person)


@router.put("/{person_id}", response_model=PersonResponse)
async def update_person(
    person_id: uuid.UUID,
    request: UpdatePersonRequest,
    handler: PersonCommandHandler = Depends(get_person_command_handler),
    _: User = Depends(require_admin),
):
    person = await handler.update(UpdatePersonCommand(
        person_id=person_id,
        full_name=request.full_name,
        tenures=[TenureData(position=t.position, start_date=t.start_date, end_date=t.end_date) for t in request.tenures] if request.tenures is not None else None,
    ))
    return _to_response(person)


@router.delete("/{person_id}", status_code=204)
async def delete_person(
    person_id: uuid.UUID,
    handler: PersonCommandHandler = Depends(get_person_command_handler),
    _: User = Depends(require_admin),
):
    await handler.delete(DeletePersonCommand(person_id=person_id))
