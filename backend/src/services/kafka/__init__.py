"""Kafka services for event-driven architecture."""
from .producer import KafkaProducerService, get_kafka_producer, shutdown_kafka_producer
from .consumer import KafkaConsumerService, get_kafka_consumer, shutdown_kafka_consumer
from .event_publisher import EventPublisher, get_event_publisher, publish_event_background
from .events import (
    TaskCreatedEvent,
    TaskUpdatedEvent,
    TaskCompletedEvent,
    TaskDeletedEvent,
    UserRegisteredEvent,
    NotificationSentEvent,
    TaskReminderEvent,
    AnalyticsEvent,
)

__all__ = [
    "KafkaProducerService",
    "KafkaConsumerService",
    "EventPublisher",
    "get_kafka_producer",
    "get_kafka_consumer",
    "get_event_publisher",
    "shutdown_kafka_producer",
    "shutdown_kafka_consumer",
    "publish_event_background",
    "TaskCreatedEvent",
    "TaskUpdatedEvent",
    "TaskCompletedEvent",
    "TaskDeletedEvent",
    "UserRegisteredEvent",
    "NotificationSentEvent",
    "TaskReminderEvent",
    "AnalyticsEvent",
]
