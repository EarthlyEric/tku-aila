import os
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langgraph.checkpoint.redis import RedisSaver

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/")
CF_AI_GATEWAY_ENDPOINT = "https://gateway.ai.cloudflare.com/v1"
CF_AI_GATEWAY_TOKEN = os.getenv("CF_AI_GATEWAY_TOKEN")
CF_ACCOUNT_ID = os.getenv("CF_ACCOUNT_ID")
CF_GATEWAY_ID = os.getenv("CF_GATEWAY_ID")
BASE_URL = f"{CF_AI_GATEWAY_ENDPOINT}/{CF_ACCOUNT_ID}/{CF_GATEWAY_ID}/compat"

class Agent:
    model = init_chat_model(
        model="google-ai-studio/gemini-2.5-flash",
        model_provider="openai",
        temperature=0,
        max_tokens=2048,
        max_retrie=2,
        api_key=CF_AI_GATEWAY_TOKEN,
        base_url=BASE_URL
    )
    base_system_prompt = """
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
    def __init__(self, channel_id: int):
        self.channel_id = channel_id
        ttl_policy = {
            "default_ttl": 86400,
            "refresh_on_read" : False
        }
        self.checkpoint = RedisSaver(redis_url=REDIS_URL, ttl=ttl_policy)
        self.checkpoint.setup()
    
    def user_input(self, message_content: str) -> dict:
        return {
            "messages": [HumanMessage(content=message_content)]
        }
            
    def parse_response(self, response: dict) -> str:
        messages = response.get('messages', [])
        if messages:
            return messages[-1].content
        return "抱歉，我無法處理您的請求。請稍後再試。 :("

class SchedulerAgent(Agent):
    def __init__(self, channel_id: int):
        super().__init__(channel_id=channel_id)
        # WIP: Add more detailed system prompt for scheduling mode
        self.system_prompt = self.base_system_prompt + """
        1. 現在是修課規劃模式。
        2. 根據學生的學習地圖，提供選課建議與學習策略。
        3. 協助學生制定學期修課計劃，考慮課程難度與先修需求。
        4. 詢問學生科系與年級，以提供更精準的建議與訪問外部資源。
        """
        self.agent = create_agent(
            model=self.model,
            system_prompt=self.system_prompt,
            checkpointer=self.checkpoint
        )
    
class SolverAgent(Agent):
    def __init__(self, channel_id: int):
        super().__init__(channel_id=channel_id)
        self.system_prompt = self.base_system_prompt + """
        1. 現在是問題解決模式，協助學生解決學習中遇到的各種問題。
        2. 提供詳細的解題步驟與相關概念說明。
        """ # Placeholder prompt
        self.agent = create_agent(
            model=self.model,
            system_prompt=self.system_prompt,
        )
    
class ExamPrepAgent(Agent):
    def __init__(self, channel_id: int):
        super().__init__(channel_id=channel_id)
        self.system_prompt = self.base_system_prompt + " You are an exam preparation assistant." # Placeholder prompt
        self.agent = create_agent(
            model=self.model,
            system_prompt=self.system_prompt,
        )
