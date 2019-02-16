"""Test loading of topics from YAML."""

import unittest

from pyinsteon import pub
from pyinsteon.topics.from_yaml import load_topics


class TestYamlLoad(unittest.TestCase):
    """Test loading of topics from YAML."""

    def setUp(self):
        """Setup the tests."""
        self.topic_mgr = pub.getDefaultTopicMgr()
        load_topics()

    def test_command_exists(self):
        """Test the command topic exists."""
        assert self.topic_mgr.getTopic('command', okIfNone=True) is not None

    def test_command_get_insteon_engine_version_direct_ack_exists(self):
        """Test the command topic exists."""
        topic = 'command.get_insteon_engine_version.direct_ack'
        assert self.topic_mgr.getTopic(topic, okIfNone=True) is not None


if __name__ == '__main__':
    unittest.main()
