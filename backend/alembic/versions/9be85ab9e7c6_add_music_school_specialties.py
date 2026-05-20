"""add_music_school_specialties

Revision ID: 9be85ab9e7c6
Revises: 7fca4f9e1636
Create Date: 2026-05-20 20:31:07.688928

"""
from typing import Sequence, Union
import uuid
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9be85ab9e7c6'
down_revision: Union[str, None] = '7fca4f9e1636'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create music_school_specialties table
    op.create_table('music_school_specialties',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('music_school_id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['music_school_id'], ['music_schools.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('music_school_id', 'name', name='uq_music_school_specialty_name')
    )

    # 2. Add specialty_id column to music_school_documents (initially nullable)
    with op.batch_alter_table('music_school_documents', schema=None) as batch_op:
        batch_op.add_column(sa.Column('specialty_id', sa.String(length=36), nullable=True))

    # 3. Data migration: copy existing string specialty column into music_school_specialties and update documents
    connection = op.get_bind()
    
    # Select all distinct music_school_id and specialty combinations
    results = connection.execute(
        sa.text("SELECT DISTINCT music_school_id, specialty FROM music_school_documents WHERE specialty IS NOT NULL AND specialty != ''")
    ).fetchall()

    specialty_ids = {} # key: (music_school_id, specialty_name.lower()), value: generated_id string
    for row in results:
        music_school_id = str(row[0])
        specialty_name = str(row[1]).strip()
        if not specialty_name:
            continue
        spec_id = str(uuid.uuid4())
        specialty_ids[(music_school_id, specialty_name.lower())] = spec_id
        
        # Insert into music_school_specialties
        connection.execute(
            sa.text("INSERT INTO music_school_specialties (id, music_school_id, name) VALUES (:id, :school_id, :name)"),
            {"id": spec_id, "school_id": music_school_id, "name": specialty_name}
        )

    # Now update music_school_documents with the new specialty_id
    doc_results = connection.execute(
        sa.text("SELECT id, music_school_id, specialty FROM music_school_documents")
    ).fetchall()
    
    for doc in doc_results:
        doc_id = str(doc[0])
        school_id = str(doc[1])
        specialty_name = str(doc[2]).strip()
        
        spec_id = specialty_ids.get((school_id, specialty_name.lower()))
        if not spec_id:
            # If for some reason it was empty or null, create a default one
            fallback_name = specialty_name if specialty_name else "Boshqa"
            spec_id = specialty_ids.get((school_id, fallback_name.lower()))
            if not spec_id:
                spec_id = str(uuid.uuid4())
                specialty_ids[(school_id, fallback_name.lower())] = spec_id
                connection.execute(
                    sa.text("INSERT INTO music_school_specialties (id, music_school_id, name) VALUES (:id, :school_id, :name)"),
                    {"id": spec_id, "school_id": school_id, "name": fallback_name}
                )
        
        connection.execute(
            sa.text("UPDATE music_school_documents SET specialty_id = :spec_id WHERE id = :doc_id"),
            {"spec_id": spec_id, "doc_id": doc_id}
        )

    # 4. Make specialty_id non-nullable, drop old specialty column, add foreign key constraint.
    with op.batch_alter_table('music_school_documents', schema=None) as batch_op:
        batch_op.alter_column('specialty_id', existing_type=sa.String(length=36), nullable=False)
        batch_op.create_foreign_key('fk_music_school_documents_specialty_id', 'music_school_specialties', ['specialty_id'], ['id'], ondelete='RESTRICT')
        batch_op.drop_column('specialty')


def downgrade() -> None:
    # 1. Add specialty column back as nullable
    with op.batch_alter_table('music_school_documents', schema=None) as batch_op:
        batch_op.add_column(sa.Column('specialty', sa.String(length=255), nullable=True))
        
    # 2. Populate specialty string from specialty_id relationship
    connection = op.get_bind()
    results = connection.execute(
        sa.text("SELECT d.id, s.name FROM music_school_documents d JOIN music_school_specialties s ON d.specialty_id = s.id")
    ).fetchall()
    
    for row in results:
        doc_id = str(row[0])
        name = str(row[1])
        connection.execute(
            sa.text("UPDATE music_school_documents SET specialty = :name WHERE id = :doc_id"),
            {"name": name, "doc_id": doc_id}
        )
        
    # 3. Make specialty column non-nullable, drop specialty_id, drop foreign key
    with op.batch_alter_table('music_school_documents', schema=None) as batch_op:
        batch_op.alter_column('specialty', existing_type=sa.String(length=255), nullable=False)
        batch_op.drop_constraint('fk_music_school_documents_specialty_id', type_='foreignkey')
        batch_op.drop_column('specialty_id')

    # 4. Drop music_school_specialties table
    op.drop_table('music_school_specialties')
