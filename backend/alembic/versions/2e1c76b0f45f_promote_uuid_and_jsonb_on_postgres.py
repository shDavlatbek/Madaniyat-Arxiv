"""promote_uuid_and_jsonb_on_postgres

Promote the legacy ``VARCHAR(36)`` UUID columns and ``JSON`` blobs to native
``uuid`` and ``jsonb`` on PostgreSQL. No-op on SQLite (the ``GUID`` /
``JSONType`` ``TypeDecorator``s keep handling that case at the app layer).

Approach: snapshot every FK in the public schema, drop them, alter every
in-scope column, then recreate the FKs from their saved DDL. All within a
single migration transaction.

Revision ID: 2e1c76b0f45f
Revises: c8a3d5e2f041
Create Date: 2026-05-15 19:49:58.699025

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "2e1c76b0f45f"
down_revision: Union[str, None] = "c8a3d5e2f041"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


GUID_COLUMNS: list[tuple[str, str]] = [
    ("appeal_types", "id"),
    ("archive_folders", "id"),
    ("archive_folders", "department_id"),
    ("archive_folders", "retention_period_id"),
    ("categories", "id"),
    ("category_fields", "id"),
    ("category_fields", "category_id"),
    ("default_fields", "id"),
    ("departments", "id"),
    ("document_attachments", "id"),
    ("document_attachments", "document_id"),
    ("document_field_values", "id"),
    ("document_field_values", "document_id"),
    ("document_field_values", "category_field_id"),
    ("document_types", "id"),
    ("documents", "id"),
    ("documents", "category_id"),
    ("documents", "person_id"),
    ("documents", "created_by"),
    ("documents", "archive_folder_id"),
    ("documents", "document_type_id"),
    ("documents", "region_id"),
    ("documents", "country_id"),
    ("documents", "reception_place_id"),
    ("documents", "appeal_type_id"),
    ("person_tenures", "id"),
    ("person_tenures", "person_id"),
    ("persons", "id"),
    ("reception_places", "id"),
    ("regions", "id"),
    ("retention_periods", "id"),
    ("users", "id"),
    ("users", "department_id"),
]

JSONB_COLUMNS: list[tuple[str, str]] = [
    ("category_fields", "options"),
    ("category_fields", "validation"),
    ("default_fields", "options"),
]


_SNAPSHOT_FKS = """
CREATE TEMP TABLE _fk_save ON COMMIT DROP AS
SELECT
    con.conname AS conname,
    cls.relname AS table_name,
    pg_get_constraintdef(con.oid) AS def
FROM pg_constraint con
JOIN pg_class cls ON con.conrelid = cls.oid
JOIN pg_namespace nsp ON cls.relnamespace = nsp.oid
WHERE con.contype = 'f' AND nsp.nspname = 'public';
"""

_DROP_FKS = """
DO $$
DECLARE r RECORD;
BEGIN
    FOR r IN SELECT conname, table_name FROM _fk_save LOOP
        EXECUTE format('ALTER TABLE %I DROP CONSTRAINT %I', r.table_name, r.conname);
    END LOOP;
END $$;
"""

_RESTORE_FKS = """
DO $$
DECLARE r RECORD;
BEGIN
    FOR r IN SELECT conname, table_name, def FROM _fk_save LOOP
        EXECUTE format('ALTER TABLE %I ADD CONSTRAINT %I %s', r.table_name, r.conname, r.def);
    END LOOP;
END $$;
"""


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    op.execute(_SNAPSHOT_FKS)
    op.execute(_DROP_FKS)

    for table, column in GUID_COLUMNS:
        op.execute(
            f'ALTER TABLE {table} ALTER COLUMN {column} TYPE uuid USING {column}::uuid'
        )

    for table, column in JSONB_COLUMNS:
        op.execute(
            f'ALTER TABLE {table} ALTER COLUMN {column} TYPE jsonb USING {column}::jsonb'
        )

    op.execute(_RESTORE_FKS)


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    op.execute(_SNAPSHOT_FKS)
    op.execute(_DROP_FKS)

    for table, column in reversed(JSONB_COLUMNS):
        op.execute(
            f'ALTER TABLE {table} ALTER COLUMN {column} TYPE json USING {column}::json'
        )

    for table, column in reversed(GUID_COLUMNS):
        op.execute(
            f'ALTER TABLE {table} ALTER COLUMN {column} TYPE varchar(36) USING {column}::text'
        )

    op.execute(_RESTORE_FKS)
