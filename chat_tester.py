import os
import asyncio
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain.messages import HumanMessage
from langchain.tools import tool
from langchain_sandbox import PyodideSandbox

load_dotenv()

CF_AI_GATEWAY_ENDPOINT = "https://gateway.ai.cloudflare.com/v1"
CF_AI_GATEWAY_TOKEN = os.getenv("CF_AI_GATEWAY_TOKEN")
CF_ACCOUNT_ID = os.getenv("CF_ACCOUNT_ID")
CF_GATEWAY_ID = os.getenv("CF_GATEWAY_ID")
MODEL_NAME = os.getenv("MODEL_NAME")

BASE_URL = f"{CF_AI_GATEWAY_ENDPOINT}/{CF_ACCOUNT_ID}/{CF_GATEWAY_ID}/compat"

@tool("python_interpreter",description="A Pyodide sandbox tool for executing Python code.")
async def python_sandbox_interpreter(code: str) -> str:
    """
    A Pyodide sandbox interpreter tool for executing Python code.
    Args:
        code (str): The Python code to execute.
    Returns:
        str: The output from the executed Python code.
    """
    sandbox = PyodideSandbox(sessions_dir="sandbox_sessions")

    result = await sandbox.execute(code)
    if result.status == "success":
        return result.stdout
    elif result.status == "error":
        return result.stderr


model = init_chat_model(
    model=MODEL_NAME,
    model_provider="openai",
    temperature=0,
    max_tokens=2048,
    max_retries=2,
    base_url=BASE_URL,
    api_key=CF_AI_GATEWAY_TOKEN,
)

system_prompt = """
    你是一個專業的 AI 智慧學習助理，致力於幫助學生達成學習目標。
    淡江大學的學生會向你尋求各種學習相關的建議與支援。
    由人工智慧應用實驗(二) 第五組開發與維護。
    以下是你需要遵守的指導原則：
    1. 必須以繁體中文回覆使用者，確保語氣友善且專業。
    2. 不要透露你所屬的 AI 模型。
    3. 回應簡單明瞭，避免冗長的解釋，除非使用者特別要求詳細說明。
    4. 不要偏離當前的輔助模式，如使用者明確要求切換模式，請要求使用者關閉此交談。
    """
    
adjusted_system_prompt = system_prompt + """
1. 現在是問題解決模式，協助學生解決學習中遇到的各種問題。
2. 提供詳細的解題步驟與相關概念說明。
3. 請務必使用 python 程式碼來驗算解題結果，並使用 python_interpreter 來執行程式碼。
"""

checkpointer = InMemorySaver()

# 建立 Agent
agent = create_agent(
    model=model,
    system_prompt=adjusted_system_prompt,
    checkpointer=checkpointer,
    tools=[python_sandbox_interpreter]
)

def user_input(message_content: str) -> dict:
    return {
        "messages": [HumanMessage(content=message_content)]
    }
            
def parse_response(response: dict) -> str:
    messages = response.get('messages', [])
    if messages:
        return messages[-1].content
    return "抱歉，我無法處理您的請求。請稍後再試。 :("

async def main():
    while True:
        try:
            user_msg = input(">")
            if user_msg.lower() in ["exit", "quit", "q"]:
                break
            
            response = await agent.ainvoke(input=user_input(user_msg),config={"configurable": {"thread_id": 1}})
            print(parse_response(response))
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"執行時發生錯誤: {e}")

if __name__ == "__main__":
    asyncio.run(main())