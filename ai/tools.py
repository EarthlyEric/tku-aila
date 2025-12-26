import logging
from langchain.tools import tool
from langchain_sandbox import PyodideSandbox
from tools.db import DBSessionManager

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

@tool("tku_course_database_query", description="A tool for querying the Tamkang University course database.")
async def tku_course_database_query(query: str) -> str:
    """
    A tool for querying the Tamkang University course database.
    banned_statements = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE"]
    Args:
        query (str): The SQL query to execute.
    Returns:
        str: The query results or error message.
    """
    logger.info(f"course_database_query Query:\n{query}")
    session_manager = DBSessionManager()
    banned_statements = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE"]
    if any(banned in query.upper() for banned in banned_statements):
        logger.error("course_database_query Error:\nAttempted to execute a banned SQL statement.")
        return "Error: Attempted to execute a banned SQL statement. Only SELECT queries are allowed."
    try:
        with session_manager.get_session() as session:
            result = session.execute(query)
            rows = result.fetchall()
            output = "\n".join([str(row) for row in rows])
            logger.info(f"course_database_query Result:\n{output}")
            return output if output else "Query executed successfully, but no results to display."
    except Exception as e:
        logger.error(f"course_database_query Error:\n{str(e)}")
        return f"An error occurred while executing the query: {str(e)}"
    