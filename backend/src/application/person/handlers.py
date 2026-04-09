from __future__ import annotations

from src.domain.person.entity import Person, PersonTenure
from src.domain.person.repository import PersonRepository
from src.domain.shared.errors import NotFoundError

from .commands import CreatePersonCommand, DeletePersonCommand, UpdatePersonCommand
from .queries import GetPersonQuery, ListActivePersonsOnDateQuery, ListPersonsQuery


class PersonCommandHandler:
    def __init__(self, person_repo: PersonRepository):
        self._person_repo = person_repo

    async def create(self, command: CreatePersonCommand) -> Person:
        person = Person(full_name=command.full_name)
        tenures = [
            PersonTenure(
                person_id=person.id,
                position=t.position,
                start_date=t.start_date,
                end_date=t.end_date,
            )
            for t in command.tenures
        ]
        person.set_tenures(tenures)
        return await self._person_repo.save(person)

    async def update(self, command: UpdatePersonCommand) -> Person:
        person = await self._person_repo.find_by_id(command.person_id)
        if not person:
            raise NotFoundError("Person", str(command.person_id))
        person.update(full_name=command.full_name)
        if command.tenures is not None:
            tenures = [
                PersonTenure(
                    person_id=person.id,
                    position=t.position,
                    start_date=t.start_date,
                    end_date=t.end_date,
                )
                for t in command.tenures
            ]
            person.set_tenures(tenures)
        return await self._person_repo.save(person)

    async def delete(self, command: DeletePersonCommand) -> None:
        await self._person_repo.delete(command.person_id)


class PersonQueryHandler:
    def __init__(self, person_repo: PersonRepository):
        self._person_repo = person_repo

    async def list_persons(self, query: ListPersonsQuery) -> list[Person]:
        return await self._person_repo.find_all(search=query.search)

    async def get_person(self, query: GetPersonQuery) -> Person:
        person = await self._person_repo.find_by_id(query.person_id)
        if not person:
            raise NotFoundError("Person", str(query.person_id))
        return person

    async def list_active_on_date(self, query: ListActivePersonsOnDateQuery) -> list[Person]:
        return await self._person_repo.find_active_on_date(query.date)
