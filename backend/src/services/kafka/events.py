"""Kafka event models for the Todo application."""
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, List
from pydantic import BaseModel, Field
import uuid


class Priority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class NotificationType(str, Enum):
    EMAIL = "EMAIL"
    PUSH = "PUSH"
    SMS = "SMS"
    IN_APP = "IN_APP"


class ReminderType(str, Enum):
    UPCOMING = "UPCOMING"
    OVERDUE = "OVERDUE"
    CUSTOM = "CUSTOM"


class BaseEvent(BaseModel):
    """Base event model with common fields."""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_timestamp: int = Field(default_factory=lambda: int(datetime.utcnow().timestamp() * 1000))

    def to_dict(self) -> Dict:
        """Convert event to dictionary for Kafka."""
        return self.model_dump()


class TaskCreatedEvent(BaseEvent):
    """Event emitted when a new task is created."""
    user_id: str
    task_id: str
    title: str
    description: Optional[str] = None
    priority: Priority = Priority.MEDIUM
    status: str = "pending"
    due_date: Optional[int] = None
    tags: List[str] = Field(default_factory=list)

    class Config:
        use_enum_values = True


class TaskUpdatedEvent(BaseEvent):
    """Event emitted when a task is updated."""
    user_id: str
    task_id: str
    changes: Dict[str, str] = Field(default_factory=dict)
    previous_values: Dict[str, Optional[str]] = Field(default_factory=dict)
    new_values: Dict[str, Optional[str]] = Field(default_factory=dict)


class TaskCompletedEvent(BaseEvent):
    """Event emitted when a task is marked as completed."""
    user_id: str
    task_id: str
    title: str
    completed_at: int = Field(default_factory=lambda: int(datetime.utcnow().timestamp() * 1000))
    duration: Optional[int] = None


class TaskDeletedEvent(BaseEvent):
    """Event emitted when a task is deleted."""
    user_id: str
    task_id: str
    title: str
    reason: Optional[str] = None


class UserRegisteredEvent(BaseEvent):
    """Event emitted when a new user registers."""
    user_id: str
    email: str
    name: Optional[str] = None
    registration_source: str = "web"


class NotificationSentEvent(BaseEvent):
    """Event emitted when a notification is sent."""
    user_id: str
    notification_type: NotificationType
    title: str
    body: str
    related_task_id: Optional[str] = None
    delivered: bool = False

    class Config:
        use_enum_values = True


class TaskReminderEvent(BaseEvent):
    """Event emitted for task reminders."""
    user_id: str
    task_id: str
    title: str
    due_date: int
    reminder_type: ReminderType

    class Config:
        use_enum_values = True


class AnalyticsEvent(BaseEvent):
    """Generic analytics event for tracking user behavior."""
    user_id: Optional[str] = None
    session_id: str
    event_name: str
    event_category: str
    properties: Dict[str, str] = Field(default_factory=dict)
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
