"""Methods to convert to and from topics."""
from ..constants import MessageFlagType


def topic_to_message_type(topic):
    """Return MessageFlagType from the topic."""
    subtopics = topic.name.split(".")
    flag = "direct" if len(subtopics) < 3 else subtopics[2]
    for msg_type in MessageFlagType:
        if flag.lower() == str(msg_type):
            return msg_type
    return MessageFlagType(0)


def topic_to_message_handler(topic, register_list):
    """Register handler to topic."""

    def register(func):
        register_list[f"send.{topic}"] = func
        return func

    return register


def topic_to_command_handler(topic, register_list):
    """Register handler to topic."""

    def register(func):
        register_list[f"send.{topic}"] = func
        return func

    return register
