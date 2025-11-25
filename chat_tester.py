from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.messages import HumanMessage

import os
from dotenv import load_dotenv
load_dotenv()
CF_AI_GATEWAY_ENDPOINT = "https://gateway.ai.cloudflare.com/v1"
CF_AI_GATEWAY_TOKEN = os.getenv("CF_AI_GATEWAY_TOKEN")
CF_ACCOUNT_ID = os.getenv("CF_ACCOUNT_ID")
CF_GATEWAY_ID = os.getenv("CF_GATEWAY_ID")
BASE_URL = f"{CF_AI_GATEWAY_ENDPOINT}/{CF_ACCOUNT_ID}/{CF_GATEWAY_ID}/compat"
print(BASE_URL)

model = init_chat_model(
        model="google-ai-studio/gemini-2.5-flash",
        model_provider="openai",
        temperature=0,
        max_tokens=2048,
        max_retries=2,
        api_key=CF_AI_GATEWAY_TOKEN,
        base_url=BASE_URL
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
    以下為當前輔助模式專有規則：
    """
agent = create_agent(model=model,system_prompt=system_prompt)

def user_input(message_content: str) -> dict:
    return {
        "messages": [HumanMessage(content=message_content)]
    }
            
def parse_response(response: dict) -> str:
    messages = response.get('messages', [])
    if messages:
        return messages[-1].content
    return "抱歉，我無法處理您的請求。請稍後再試。 :("

while True:
    i = input(">")
    response = agent.invoke(input=user_input(i))
    print(parse_response(response))