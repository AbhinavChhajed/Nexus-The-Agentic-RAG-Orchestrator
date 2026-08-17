"""
Python REPL tool — executes Python code in a sandboxed interpreter.
"""

from langchain_core.tools import tool
from langchain_experimental.utilities import PythonREPL

_python_repl = PythonREPL()


@tool
def python_interpreter(code: str) -> str:
    """
    A Python shell. Use this to execute python commands.
    Input should be a valid python script.
    Use this for math, data analysis, or processing text.
    ALWAYS print(...) your final result so I can see it.
    """
    try:
        result = _python_repl.run(code)
        return f"Executed:\n{result}"
    except Exception as e:
        return f"Error: {e}"
