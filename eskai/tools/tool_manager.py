from typing import Dict, Any


class ToolManager:
    """
    Dynamic tool manager for ESKAI framework.
    Responsible for instantiating and managing tool instances.
    """

    def __init__(self):
        self.tools: Dict[str, Any] = {}

    def register_tool(self, name: str, tool_cls: Any, **kwargs) -> None:
        """
        Register a new tool by name.
        """
        self.tools[name] = tool_cls(name=name, **kwargs)

    def get_tool(self, name: str) -> Any:
        """
        Retrieve a registered tool instance by name.
        """
        return self.tools.get(name)
