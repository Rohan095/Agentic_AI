from agent.tool import Tool


def calculate(expression: str):
    # Basic validation to prevent code injection
    if not all(c.isdigit() or c in "+-*/(). " for c in expression):
        raise ValueError("Invalid characters in expression")
    try:
        return eval(expression)
    except Exception as e:
        raise ValueError(f"Error evaluating expression: {e}")


calculator_tool = Tool(
    name="calculator",
    description="Evaluate a mathematical expression and return the numeric result.",
    parameters = {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "The mathematical expression to evaluate"
            }
        },
        "required": ["expression"]
    },
    function=calculate
)