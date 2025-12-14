"""Create tasks table

Revision ID: 001
Revises:
Create Date: 2025-12-12 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Create tasks table with user isolation support.

    Columns:
    - id: SERIAL primary key
    - user_id: UUID foreign key to users table (indexed for query performance)
    - title: VARCHAR(200) non-null task title
    - description: TEXT nullable task description
    - is_completed: BOOLEAN default false
    - created_at: TIMESTAMP default now()

    Indexes:
    - idx_tasks_user_id: For filtering tasks by user (Golden Rule enforcement)
    - idx_tasks_created_at: For ordering tasks by creation date (DESC)
    """
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('user_id', sa.String(), nullable=False),  # UUID as string
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_completed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )

    # Create index on user_id for efficient user isolation queries
    # This is CRITICAL for the Golden Rule: WHERE user_id = current_user
    op.create_index(
        'idx_tasks_user_id',
        'tasks',
        ['user_id']
    )

    # Create index on created_at for efficient ordering (DESC)
    op.create_index(
        'idx_tasks_created_at',
        'tasks',
        ['created_at'],
        postgresql_ops={'created_at': 'DESC'}
    )


def downgrade() -> None:
    """
    Drop tasks table and all indexes.
    """
    op.drop_index('idx_tasks_created_at', table_name='tasks')
    op.drop_index('idx_tasks_user_id', table_name='tasks')
    op.drop_table('tasks')
