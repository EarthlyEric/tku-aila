import logging
from langchain.tools import tool
from langchain_sandbox import PyodideSandbox

logger = logging.getLogger("tku-aila")

@tool("python_sandbox",description="A Pyodide sandbox tool for executing Python code.")
async def python_sandbox_interpreter(code: str) -> str:
    """
    A Pyodide sandbox interpreter tool for executing Python code.
    Args:
        code (str): The Python code to execute.
    Returns:
        str: The output from the executed Python code.
    """
    sandbox = PyodideSandbox(sessions_dir="sandbox_sessions")
    logger.info(f"python_sandbox Code:\n{code}")
    
    result = await sandbox.execute(code)
    if result.status == "success":
        logger.info(f"python_sandbox Result:\n{result.stdout}")
        return result.stdout
    elif result.status == "error":
        logger.error(f"python_sandbox Error:\n{result.stderr}")
        return result.stderr
    

    