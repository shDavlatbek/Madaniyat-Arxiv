import uuid

from fastapi import APIRouter, Depends

from src.api.dependencies import get_category_command_handler, get_category_query_handler
from src.api.middleware.auth import get_current_user, require_admin
from src.api.schemas.category import (
    AddFieldRequest,
    CategoryFieldResponse,
    CategoryListResponse,
    CategoryResponse,
    CopyCategoryRequest,
    CreateCategoryRequest,
    CreateDefaultFieldRequest,
    DefaultFieldListResponse,
    DefaultFieldResponse,
    UpdateCategoryRequest,
    UpdateDefaultFieldRequest,
    UpdateFieldRequest,
)
from src.application.category.commands import (
    AddFieldCommand,
    CopyCategoryCommand,
    CreateCategoryCommand,
    CreateDefaultFieldCommand,
    DeleteCategoryCommand,
    DeleteDefaultFieldCommand,
    DeleteFieldCommand,
    UpdateCategoryCommand,
    UpdateDefaultFieldCommand,
    UpdateFieldCommand,
)
from src.application.category.handlers import CategoryCommandHandler, CategoryQueryHandler
from src.application.category.queries import GetCategoryFieldsQuery, ListAllCategoriesQuery, ListCategoriesByYearQuery, ListDefaultFieldsQuery
from src.domain.category.entity import Category, CategoryField, DefaultField
from src.domain.user.entity import User

router = APIRouter(tags=["categories"])


def _field_to_response(f: CategoryField) -> CategoryFieldResponse:
    return CategoryFieldResponse(
        id=f.id, category_id=f.category_id, name=f.name, label=f.label,
        field_type=f.field_type.value, is_required=f.is_required, sort_order=f.sort_order,
        options=f.options, placeholder=f.placeholder, validation=f.validation, created_at=f.created_at,
    )


def _to_response(cat: Category) -> CategoryResponse:
    return CategoryResponse(
        id=cat.id, name=cat.name, code=cat.code, description=cat.description,
        sort_order=cat.sort_order, year_ids=cat.year_ids,
        fields=[_field_to_response(f) for f in cat.fields],
        created_at=cat.created_at, updated_at=cat.updated_at,
    )


def _default_field_to_response(f: DefaultField) -> DefaultFieldResponse:
    return DefaultFieldResponse(
        id=f.id, name=f.name, label=f.label, field_type=f.field_type.value,
        is_required=f.is_required, sort_order=f.sort_order, options=f.options,
        placeholder=f.placeholder, created_at=f.created_at,
    )


@router.get("/api/years/{year_id}/categories", response_model=CategoryListResponse)
async def list_categories_by_year(
    year_id: int,
    handler: CategoryQueryHandler = Depends(get_category_query_handler),
    _: User = Depends(get_current_user),
):
    categories = await handler.list_by_year(ListCategoriesByYearQuery(year_id=year_id))
    return CategoryListResponse(items=[_to_response(c) for c in categories])


@router.get("/api/categories", response_model=CategoryListResponse)
async def list_all_categories(
    handler: CategoryQueryHandler = Depends(get_category_query_handler),
    _: User = Depends(get_current_user),
):
    categories = await handler.list_all(ListAllCategoriesQuery())
    return CategoryListResponse(items=[_to_response(c) for c in categories])


@router.post("/api/categories", response_model=CategoryResponse, status_code=201)
async def create_category(
    request: CreateCategoryRequest,
    handler: CategoryCommandHandler = Depends(get_category_command_handler),
    _: User = Depends(require_admin),
):
    category = await handler.create(CreateCategoryCommand(
        name=request.name, code=request.code, description=request.description,
        sort_order=request.sort_order, year_ids=request.year_ids,
    ))
    return _to_response(category)


@router.put("/api/categories/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: uuid.UUID,
    request: UpdateCategoryRequest,
    handler: CategoryCommandHandler = Depends(get_category_command_handler),
    _: User = Depends(require_admin),
):
    category = await handler.update(UpdateCategoryCommand(
        category_id=category_id, name=request.name, code=request.code,
        description=request.description, sort_order=request.sort_order,
        year_id=request.year_id,
    ))
    return _to_response(category)


@router.delete("/api/categories/{category_id}", status_code=204)
async def delete_category(
    category_id: uuid.UUID,
    handler: CategoryCommandHandler = Depends(get_category_command_handler),
    _: User = Depends(require_admin),
):
    await handler.delete(DeleteCategoryCommand(category_id=category_id))


@router.post("/api/categories/{category_id}/copy", response_model=CategoryResponse, status_code=201)
async def copy_category(
    category_id: uuid.UUID,
    request: CopyCategoryRequest,
    handler: CategoryCommandHandler = Depends(get_category_command_handler),
    _: User = Depends(require_admin),
):
    category = await handler.copy_category(CopyCategoryCommand(
        source_category_id=category_id, target_year_ids=request.target_year_ids,
    ))
    return _to_response(category)


@router.get("/api/categories/{category_id}/fields", response_model=list[CategoryFieldResponse])
async def get_category_fields(
    category_id: uuid.UUID,
    handler: CategoryQueryHandler = Depends(get_category_query_handler),
    _: User = Depends(get_current_user),
):
    fields = await handler.get_fields(GetCategoryFieldsQuery(category_id=category_id))
    return [_field_to_response(f) for f in fields]


@router.post("/api/categories/{category_id}/fields", response_model=CategoryFieldResponse, status_code=201)
async def add_field(
    category_id: uuid.UUID,
    request: AddFieldRequest,
    handler: CategoryCommandHandler = Depends(get_category_command_handler),
    _: User = Depends(require_admin),
):
    field = await handler.add_field(AddFieldCommand(
        category_id=category_id, name=request.name, label=request.label,
        field_type=request.field_type, is_required=request.is_required,
        sort_order=request.sort_order, options=request.options,
        placeholder=request.placeholder, validation=request.validation,
    ))
    return _field_to_response(field)


@router.put("/api/categories/{category_id}/fields/{field_id}", response_model=CategoryFieldResponse)
async def update_field(
    category_id: uuid.UUID,
    field_id: uuid.UUID,
    request: UpdateFieldRequest,
    handler: CategoryCommandHandler = Depends(get_category_command_handler),
    _: User = Depends(require_admin),
):
    field = await handler.update_field(UpdateFieldCommand(
        field_id=field_id, label=request.label, field_type=request.field_type,
        is_required=request.is_required, sort_order=request.sort_order,
        options=request.options, placeholder=request.placeholder, validation=request.validation,
    ))
    return _field_to_response(field)


@router.delete("/api/categories/{category_id}/fields/{field_id}", status_code=204)
async def delete_field(
    category_id: uuid.UUID,
    field_id: uuid.UUID,
    handler: CategoryCommandHandler = Depends(get_category_command_handler),
    _: User = Depends(require_admin),
):
    await handler.delete_field(DeleteFieldCommand(field_id=field_id))


# --- Default Fields CRUD ---

@router.get("/api/default-fields", response_model=DefaultFieldListResponse)
async def list_default_fields(
    handler: CategoryQueryHandler = Depends(get_category_query_handler),
    _: User = Depends(require_admin),
):
    fields = await handler.list_default_fields(ListDefaultFieldsQuery())
    return DefaultFieldListResponse(items=[_default_field_to_response(f) for f in fields])


@router.post("/api/default-fields", response_model=DefaultFieldResponse, status_code=201)
async def create_default_field(
    request: CreateDefaultFieldRequest,
    handler: CategoryCommandHandler = Depends(get_category_command_handler),
    _: User = Depends(require_admin),
):
    field = await handler.create_default_field(CreateDefaultFieldCommand(
        name=request.name, label=request.label, field_type=request.field_type,
        is_required=request.is_required, sort_order=request.sort_order,
        options=request.options, placeholder=request.placeholder,
    ))
    return _default_field_to_response(field)


@router.put("/api/default-fields/{field_id}", response_model=DefaultFieldResponse)
async def update_default_field(
    field_id: uuid.UUID,
    request: UpdateDefaultFieldRequest,
    handler: CategoryCommandHandler = Depends(get_category_command_handler),
    _: User = Depends(require_admin),
):
    field = await handler.update_default_field(UpdateDefaultFieldCommand(
        field_id=field_id, label=request.label, field_type=request.field_type,
        is_required=request.is_required, sort_order=request.sort_order,
        options=request.options, placeholder=request.placeholder,
    ))
    return _default_field_to_response(field)


@router.delete("/api/default-fields/{field_id}", status_code=204)
async def delete_default_field(
    field_id: uuid.UUID,
    handler: CategoryCommandHandler = Depends(get_category_command_handler),
    _: User = Depends(require_admin),
):
    await handler.delete_default_field(DeleteDefaultFieldCommand(field_id=field_id))
