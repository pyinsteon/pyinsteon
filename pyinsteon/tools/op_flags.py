"""Command line interface for Operation Flag Management."""

from .tools_base import ToolsBase


class ToolsOpFlags(ToolsBase):
    """Command line interface for Operation Flag Management."""

    def do_print_args(self, *args, **kwargs):
        """Delete me."""
        print(self.device)
        print(self.host)
        print(self.username)
