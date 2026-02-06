"""Tag service layer for business logic."""

from typing import List, Optional
from sqlmodel import Session, select
from datetime import datetime

from ..models.tag import Tag, TagCreate
from ..models.task_tag import TaskTag


class TagService:
    """
    Tag service for handling tag-related business logic.

    All methods enforce user isolation - tags are always filtered by user_id.
    """

    @staticmethod
    def create_tag(
        session: Session, tag_data: TagCreate, user_id: str
    ) -> Tag:
        """
        Create a new tag for a user (if it doesn't already exist).

        Args:
            session: Database session
            tag_data: Tag creation data (name)
            user_id: UUID of the authenticated user

        Returns:
            Created or existing Tag instance

        Security:
            user_id is ALWAYS from JWT token, never from request body
        """
        # Check if tag with this name already exists for this user
        existing_tag = session.exec(
            select(Tag).where(
                Tag.user_id == user_id,
                Tag.name == tag_data.name.lower()  # Case-insensitive
            )
        ).first()

        if existing_tag:
            return existing_tag

        # Create new tag
        tag = Tag(
            name=tag_data.name.lower(),  # Store in lowercase for consistency
            user_id=user_id,
            created_at=datetime.utcnow(),
        )

        session.add(tag)
        session.commit()
        session.refresh(tag)
        return tag

    @staticmethod
    def get_tags_by_user(
        session: Session, user_id: str, search_query: Optional[str] = None
    ) -> List[Tag]:
        """
        Get all tags for a user with optional search filter.

        Args:
            session: Database session
            user_id: UUID of the authenticated user
            search_query: Optional search string for tag name

        Returns:
            List of Tag instances

        Security:
            GOLDEN RULE: Always filter by user_id to enforce isolation
        """
        statement = select(Tag).where(Tag.user_id == user_id)

        if search_query:
            statement = statement.where(
                Tag.name.contains(search_query.lower())
            )

        statement = statement.order_by(Tag.name)

        tags = session.exec(statement).all()
        return list(tags)

    @staticmethod
    def get_tag_by_id(
        session: Session, tag_id: int, user_id: str
    ) -> Optional[Tag]:
        """
        Get a specific tag by ID if it belongs to the user.

        Args:
            session: Database session
            tag_id: ID of the tag
            user_id: UUID of the authenticated user

        Returns:
            Tag instance if found and belongs to user, None otherwise

        Security:
            GOLDEN RULE: Always verify tag ownership with user_id filter
        """
        statement = select(Tag).where(
            Tag.id == tag_id, Tag.user_id == user_id
        )
        tag = session.exec(statement).first()
        return tag

    @staticmethod
    def delete_tag(session: Session, tag_id: int, user_id: str) -> bool:
        """
        Delete a tag if it belongs to the user.

        This also removes all task-tag associations for this tag.

        Args:
            session: Database session
            tag_id: ID of the tag to delete
            user_id: UUID of the authenticated user

        Returns:
            True if tag was deleted, False if not found or not owned by user

        Security:
            GOLDEN RULE: Verify ownership before deletion
        """
        tag = TagService.get_tag_by_id(session, tag_id, user_id)
        if not tag:
            return False

        # Delete all task-tag associations first
        session.exec(
            select(TaskTag).where(TaskTag.tag_id == tag_id)
        ).all()
        for task_tag in session.exec(
            select(TaskTag).where(TaskTag.tag_id == tag_id)
        ).all():
            session.delete(task_tag)

        # Delete the tag
        session.delete(tag)
        session.commit()
        return True

    @staticmethod
    def add_tag_to_task(
        session: Session, task_id: int, tag_id: int
    ) -> TaskTag:
        """
        Add a tag to a task (create task-tag association).

        Args:
            session: Database session
            task_id: ID of the task
            tag_id: ID of the tag

        Returns:
            Created TaskTag instance

        Note:
            Caller must verify task and tag ownership before calling this method
        """
        # Check if association already exists
        existing = session.exec(
            select(TaskTag).where(
                TaskTag.task_id == task_id,
                TaskTag.tag_id == tag_id
            )
        ).first()

        if existing:
            return existing

        # Create new association
        task_tag = TaskTag(
            task_id=task_id,
            tag_id=tag_id,
            created_at=datetime.utcnow(),
        )

        session.add(task_tag)
        session.commit()
        session.refresh(task_tag)
        return task_tag

    @staticmethod
    def remove_tag_from_task(
        session: Session, task_id: int, tag_id: int
    ) -> bool:
        """
        Remove a tag from a task (delete task-tag association).

        Args:
            session: Database session
            task_id: ID of the task
            tag_id: ID of the tag

        Returns:
            True if association was deleted, False if not found

        Note:
            Caller must verify task and tag ownership before calling this method
        """
        task_tag = session.exec(
            select(TaskTag).where(
                TaskTag.task_id == task_id,
                TaskTag.tag_id == tag_id
            )
        ).first()

        if not task_tag:
            return False

        session.delete(task_tag)
        session.commit()
        return True

    @staticmethod
    def get_tags_for_task(
        session: Session, task_id: int
    ) -> List[Tag]:
        """
        Get all tags associated with a task.

        Args:
            session: Database session
            task_id: ID of the task

        Returns:
            List of Tag instances

        Note:
            Caller must verify task ownership before calling this method
        """
        # Get all task-tag associations for this task
        task_tags = session.exec(
            select(TaskTag).where(TaskTag.task_id == task_id)
        ).all()

        # Get the actual tag objects
        tag_ids = [tt.tag_id for tt in task_tags]
        if not tag_ids:
            return []

        tags = session.exec(
            select(Tag).where(Tag.id.in_(tag_ids))
        ).all()

        return list(tags)

    @staticmethod
    def get_popular_tags(
        session: Session, user_id: str, limit: int = 10
    ) -> List[dict]:
        """
        Get most frequently used tags for a user.

        Args:
            session: Database session
            user_id: UUID of the authenticated user
            limit: Maximum number of tags to return

        Returns:
            List of dicts with tag info and usage count
        """
        from sqlalchemy import func

        # Get tag usage counts
        statement = (
            select(Tag, func.count(TaskTag.id).label("usage_count"))
            .join(TaskTag, Tag.id == TaskTag.tag_id, isouter=True)
            .where(Tag.user_id == user_id)
            .group_by(Tag.id)
            .order_by(func.count(TaskTag.id).desc())
            .limit(limit)
        )

        results = session.exec(statement).all()

        return [
            {
                "id": tag.id,
                "name": tag.name,
                "usage_count": usage_count or 0,
            }
            for tag, usage_count in results
        ]
