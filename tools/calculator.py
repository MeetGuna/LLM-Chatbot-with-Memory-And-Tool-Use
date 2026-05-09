from langchain.tools import tool
import math


@tool
def calculator_tool(expression: str) -> str:
    """
    Evaluates a mathematical expression safely.
    Use this for any arithmetic, percentages, powers, square roots, or basic maths.
    Examples: '2 + 2', '15% of 3000', 'sqrt(144)', '2 ** 10'
    """
    try:
        # Safe evaluation — only allow math operations
        allowed_names = {k: v for k, v in math.__dict__.items() if not k.startswith("_")}
        allowed_names["abs"] = abs
        allowed_names["round"] = round

        # Replace common natural language patterns
        expression = expression.replace("^", "**")
        expression = expression.replace("×", "*")
        expression = expression.replace("÷", "/")

        # Handle "X% of Y" pattern
        if "% of" in expression.lower():
            parts = expression.lower().replace("% of", "* 0.01 *").split("* 0.01 *")
            if len(parts) == 2:
                expression = f"{parts[0].strip()} * 0.01 * {parts[1].strip()}"

        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return f"Result: {result}"
    except Exception as e:
        return f"Could not evaluate '{expression}': {str(e)}"
