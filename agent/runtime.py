class AgentRuntime:
    def __init__(self, registry):
        self.registry = registry

    def execute_tool(self, tool_name, arguments):
        tool = self.registry.get(tool_name)

        if tool is None:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found"
            }

        required = tool.parameters.get("required", [])

        for parameter in required:
            if parameter not in arguments:
                return {
                    "success": False,
                    "error": f"Missing required parameter: {parameter}"
                }

        result = tool.function(**arguments)

        return {
            "success": True,
            "tool": tool_name,
            "result": result
        }