import asyncio
import uuid
from src.infrastructure.persistence.database import async_session
from src.infrastructure.persistence.models import SearchIndexJobModel

async def run():
    async with async_session() as session:
        session.add(SearchIndexJobModel(
            document_id=uuid.UUID("33333333-3333-3333-3333-333333333333"),
            op="index",
            entity_type="music_school"
        ))
        session.add(SearchIndexJobModel(
            document_id=uuid.UUID("44444444-4444-4444-4444-444444444444"),
            op="index",
            entity_type="music_school"
        ))
        await session.commit()
    print("Outbox search index jobs created successfully for mock documents!")

if __name__ == "__main__":
    asyncio.run(run())
