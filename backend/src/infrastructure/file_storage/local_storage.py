import os
import uuid
from pathlib import Path

import aiofiles

from src.infrastructure.config import settings


class FileStorageService:
    def __init__(self):
        self._base_dir = Path(settings.upload_dir)

    async def save_file(self, file_content: bytes, filename: str, document_id: uuid.UUID) -> str:
        dir_path = self._base_dir / str(document_id)
        dir_path.mkdir(parents=True, exist_ok=True)
        file_path = dir_path / filename
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(file_content)
        return str(file_path)

    async def get_file_path(self, stored_path: str) -> Path | None:
        path = Path(stored_path)
        return path if path.exists() else None

    async def delete_file(self, stored_path: str) -> None:
        path = Path(stored_path)
        if path.exists():
            path.unlink()
            # Remove parent dir if empty
            parent = path.parent
            if parent.exists() and not any(parent.iterdir()):
                parent.rmdir()
