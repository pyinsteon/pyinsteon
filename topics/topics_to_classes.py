"""Export topics to classes."""

import os

from pubsub import pub
from pubsub.utils.yamltopicdefnprovider import (
    TOPIC_TREE_FROM_FILE,
    YamlTopicDefnProvider,
)

FILENAME = "topics.yaml"


def load_topics(file):
    """Load topics from a YAML file."""
    provider = YamlTopicDefnProvider(file, format=TOPIC_TREE_FROM_FILE)
    pub.clearTopicDefnProviders()
    pub.addTopicDefnProvider(provider)
    pub.instantiateAllDefinedTopics(provider)


def export_classes():
    """Export the current topics to classes."""
    PATH_TO_FILE = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__), FILENAME)
    )
    load_topics(PATH_TO_FILE)

    pub.exportTopicTreeSpec("topics")


if __name__ == "__main__":
    export_classes()
