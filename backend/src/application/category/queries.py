from __future__ import annotations

import uuid
from dataclasses import dataclass


@dataclass
class ListCategoriesByYearQuery:
    year_id: int


@dataclass
class ListAllCategoriesQuery:
    pass


@dataclass
class GetCategoryFieldsQuery:
    category_id: uuid.UUID
