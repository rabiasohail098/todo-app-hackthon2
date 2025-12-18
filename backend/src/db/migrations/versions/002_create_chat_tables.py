"""Create conversations and messages tables for AI chatbot

Revision ID: 002
Revises: 001
Create Date: 2025-12-16 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Create conversations and messages tables for AI chatbot feature.

    Conversations Table:
    - id: UUID primary key
    - user_id: UUID for user isolation (indexed)
    - created_at: TIMESTAMP for ordering

    Messages Table:
    - id: UUID primary key
    - conversation_id: UUID foreign key to conversations
    - role: VARCHAR(20) - 'user' or 'assistant'
    - content: TEXT for message content
    - created_at: TIMESTAMP for ordering
    """
    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', sa.String(36), nullable=False),  # UUID as string
        sa.Column('user_id', sa.String(36), nullable=False),  # UUID as string
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for conversations
    op.create_index(
        'idx_conversations_user_id',
        'conversations',
        ['user_id']
    )
    op.create_index(
        'idx_conversations_created_at',
        'conversations',
        ['created_at'],
        postgresql_ops={'created_at': 'DESC'}
    )

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.String(36), nullable=False),  # UUID as string
        sa.Column('conversation_id', sa.String(36), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.CheckConstraint("role IN ('user', 'assistant')", name='check_message_role')
    )

    # Create indexes for messages
    op.create_index(
        'idx_messages_conversation_id',
        'messages',
        ['conversation_id']
    )
    op.create_index(
        'idx_messages_created_at',
        'messages',
        ['created_at']
    )
    # Composite index for efficient history fetch
    op.create_index(
        'idx_messages_conv_created',
        'messages',
        ['conversation_id', 'created_at']
    )


def downgrade() -> None:
    """
    Drop messages and conversations tables.
    """
    # Drop messages table first (has foreign key)
    op.drop_index('idx_messages_conv_created', table_name='messages')
    op.drop_index('idx_messages_created_at', table_name='messages')
    op.drop_index('idx_messages_conversation_id', table_name='messages')
    op.drop_table('messages')

    # Drop conversations table
    op.drop_index('idx_conversations_created_at', table_name='conversations')
    op.drop_index('idx_conversations_user_id', table_name='conversations')
    op.drop_table('conversations')
