"""Methods to convert to and from topics."""

from .. import pub
from ..constants import MessageFlagType

topic_mgr = pub.getDefaultTopicMgr()


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
        # params = inspect.signature(func).parameters
        # arg_spec = {}
        # for name, param in params.items():
        #     desc = _map_param_to_description(name, param.annotation)
        #     arg_spec[name] = desc

        # topic_item = topic_mgr.getOrCreateTopic(f"send.{topic}")
        # if not topic_item.hasMDS:
        #     required = list(arg_spec)
        #     if "topic" in required:
        #         required.remove("topic")
        #     # topic_item.setMsgArgSpec(arg_spec, required)

        return func

    return register


def topic_to_command_handler(topic, register_list):
    """Register handler to topic."""

    def register(func):
        register_list[f"send.{topic}"] = func
        # params = inspect.signature(func).parameters
        # arg_spec = {}
        # for name, param in params.items():
        #     desc = _map_param_to_description(name, param.annotation)
        #     arg_spec[name] = desc

        # topic_item = topic_mgr.getOrCreateTopic(f"send.{topic}")
        # if not topic_item.hasMDS:
        #     required = list(arg_spec)
        #     if "topic" in required:
        #         required.remove("topic")
        #     # topic_item.setMsgArgSpec(arg_spec, required)
        return func

    return register
