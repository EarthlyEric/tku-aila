import re
import logging
from langchain.tools import tool
from pydantic import BaseModel, Field
from langchain_sandbox import PyodideSandbox
from sqlalchemy import text
from tools.db import DBSessionManager

logger = logging.getLogger("tku-aila")

class PythonInterpreterArgs(BaseModel):
    code: str = Field(description="The Python code to execute.")

class TKUCourseDatabaseQueryArgs(BaseModel):
    query: str = Field(description="The SQL query to execute on the Tamkang University course database. banned_statements = [\"INSERT\", \"UPDATE\", \"DELETE\", \"DROP\", \"ALTER\", \"CREATE\"]")

@tool("python",description="A Pyodide sandbox tool for executing Python code.", args_schema=PythonInterpreterArgs)
async def python_interpreter(code: str) -> str:
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

@tool("tku_course_database_query", description="A tool for querying the Tamkang University course database.", args_schema=TKUCourseDatabaseQueryArgs)
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
    query_normalized = re.sub(r'/\*.*?\*/', '', query, flags=re.DOTALL) # Remove block comments
    query_normalized = re.sub(r'--.*$', '', query_normalized, flags=re.MULTILINE) # Remove line comments
    query_normalized = re.sub(r'\s+', '', query_normalized) # Remove all whitespace

    if any(banned in query_normalized.upper() for banned in banned_statements):
        logger.error("course_database_query Error:Attempted to execute a banned SQL statement.")
        return "Error: Attempted to execute a banned SQL statement. Only SELECT queries are allowed."
    
    try:
        with session_manager.get_session() as session:
            result = session.execute(text(query)) 
            
            rows = result.fetchall()
            output = "\n".join([str(row) for row in rows])
            logger.info(f"course_database_query Result:\n{output}")
            return output if output else "Query executed successfully, but no results to display."
    except Exception as e:
        logger.error(f"course_database_query Error:\n{str(e)}")
        return f"An error occurred while executing the query: {str(e)}"
    