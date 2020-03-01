"""Import a Topic Definition from yaml."""

import os

from pubsub import pub
from pubsub.utils.yamltopicdefnprovider import (
    TOPIC_TREE_FROM_FILE,
    YamlTopicDefnProvider,
)

FILENAME = "topics.yaml"
PATH_TO_FILE = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__), FILENAME)
)


def load_topics(file=PATH_TO_FILE):
    """Load topics from a YAML file."""
    provider = YamlTopicDefnProvider(file, format=TOPIC_TREE_FROM_FILE)
    pub.clearTopicDefnProviders()
    pub.addTopicDefnProvider(provider)
    pub.instantiateAllDefinedTopics(provider)
