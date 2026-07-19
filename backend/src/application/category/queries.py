from __future__ import annotations

import uuid
from dataclasses import dataclass


@dataclass
class ListAllCategoriesQuery:
    pass


@dataclass
class GetCategoryFieldsQuery:
    category_id: uuid.UUID


@dataclass
class ListDefaultFieldsQuery:
    pass
