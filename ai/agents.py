import os
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langchain.agents.middleware import SummarizationMiddleware, ContextEditingMiddleware , ClearToolUsesEdit
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.redis import AsyncRedisSaver

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/")
CF_AI_GATEWAY_ENDPOINT = "https://gateway.ai.cloudflare.com/v1"
CF_AI_GATEWAY_TOKEN = os.getenv("CF_AI_GATEWAY_TOKEN")
CF_ACCOUNT_ID = os.getenv("CF_ACCOUNT_ID")
CF_GATEWAY_ID = os.getenv("CF_GATEWAY_ID")
BASE_URL = f"{CF_AI_GATEWAY_ENDPOINT}/{CF_ACCOUNT_ID}/{CF_GATEWAY_ID}/compat"
MODEL_NAME = os.getenv("MODEL_NAME")
SMALL_MODEL_NAME = os.getenv("SMALL_MODEL_NAME")

class Agent:
    model = init_chat_model(
        model=MODEL_NAME,
        model_provider="openai",
        temperature=0,
        max_tokens=3072,
        max_retries=2,
        api_key=CF_AI_GATEWAY_TOKEN,
        base_url=BASE_URL
    )
    small_model = init_chat_model(
        model=SMALL_MODEL_NAME,
        model_provider="openai",
        temperature=0,
        max_tokens=3072,
        max_retries=2,
        api_key=CF_AI_GATEWAY_TOKEN,
        base_url=BASE_URL
    )
    
class WorkerAgent(Agent):
    def __init__(self, system_prompt: str, tools: list = []):
        self.checkpoint = InMemorySaver()
        self.system_prompt = system_prompt
        self.agent = create_agent(
            model=self.model,
            system_prompt=self.system_prompt,
            tools=tools,
            middleware=[
                SummarizationMiddleware(
                    model=self.small_model,
                    max_tokens_before_summary= 2000,
                ),
                ContextEditingMiddleware(
                    edits=[
                        ClearToolUsesEdit(
                            trigger=2500,
                            keep=3,
                        ),
                    ],
                ),
            ],
            checkpointer=self.checkpoint
        )
    
    def user_input(self, message_content: str) -> dict:
        return {
            "messages": [HumanMessage(content=message_content)]
        }
    
    def parse_response(self, response: dict) -> str:
        messages = response.get('messages', [])
        if messages:
            return messages[-1].content
        return "抱歉，我無法處理您的請求。請稍後再試。 :("
      
class ChatAgent(Agent):
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
        self.checkpoint = AsyncRedisSaver(redis_url=REDIS_URL, ttl=ttl_policy)
    
    def user_input(self, message_content: str) -> dict:
        return {
            "messages": [HumanMessage(content=message_content)]
        }
            
    def parse_response(self, response: dict) -> str:
        messages = response.get('messages', [])
        if messages:
            return messages[-1].content
        return "抱歉，我無法處理您的請求。請稍後再試。 :("

class SchedulerAgent(ChatAgent):
    def __init__(self, channel_id: int):
        from .tools import tku_course_database_query
        super().__init__(channel_id=channel_id)
        self.system_prompt = self.base_system_prompt + """
        1. 現在是修課規劃模式。
        2. 協助學生制定學期修課計劃，考慮課程難度與先修需求。
        3. 詢問學生科系與年級，以提供更精準的建議與訪問外部資源。
        4. 使用 tku_course_database_query 的 SQL 工具來查詢淡江大學的課程資訊，先查詢 metadata 表以獲取最新的學年與學期資訊。。
        以下為資料庫查詢工具的使用說明：
            - 工具名稱：tku_course_database_query
            - 禁止SQL語句列表: ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE"]
            - 僅允許使用 SELECT 語句來查詢課程資料。
            - 【重要】所有 SELECT 查詢必須加上 "LIMIT 10" 以避免回傳過多資料導致錯誤。
            - 若資料不足，再進行第二次更精確的查詢。
            - 注意系別、年級等條件需與學生需求相符，特別注意人工智慧學系與AI系要以 人工智慧學系 查詢。
            - 回傳結果時，請整理成易讀的格式，並提供必要的解釋與建議。
            - Database schema 包含以下主要欄位：
                table name:courses
                    "id": 唯一識別碼(無需使用)
                    "department": 系別
                    "grade": 年級
                    "serial_no": 開課序號
                    "course_id": 科目編號
                    "specialty": 專業別
                    "semester": 學期序
                    "class_type": 班別
                    "group_type": 分組別
                    "required_elective_type": 必選修 (Required/Elective)
                    "credits": 學分數
                    "group_type": 群別
                    "course_name": 科目名稱
                    "people_limit": 人數設限
                    "instructor": 授課教師
                    "time_place": 星期/節次/教室
                table name:metadata
                    "id": 唯一識別碼，固定為1
                    "year": 學年
                    "semester": 學期
        5. 在回應中引用查詢結果，並根據學生需求提供具體的選課建議。
        """
        self.agent = create_agent(
            model=self.model,
            system_prompt=self.system_prompt,
            middleware=[
                SummarizationMiddleware(
                    model=self.small_model,
                    max_tokens_before_summary= 2000,
                ),
                ContextEditingMiddleware(
                    edits=[
                        ClearToolUsesEdit(
                            trigger=2500,
                            keep=1,
                        ),
                    ],
                ),
            ],
            tools=[tku_course_database_query],
            checkpointer=self.checkpoint
        )
    
class SolverAgent(ChatAgent):
    def __init__(self, channel_id: int):
        from .tools import python_interpreter
        super().__init__(channel_id=channel_id)
        self.system_prompt = self.base_system_prompt + """
        1. 現在是問題解決模式，協助學生解決學習中遇到的各種問題。
        2. 提供詳細的解題步驟與相關概念說明。
        3. 請務必使用 python 程式碼來驗算解題結果，並使用 python 來執行程式碼。
        以下為 python 程式碼執行工具的使用說明：
            - 工具名稱：python
            - 僅允許使用 python 程式碼來進行計算與驗算。
            - 回傳結果時，請整理成易讀的格式，並提供必要的解釋與建議。
        4. 在回應中引用程式碼執行結果，並根據學生需求提供具體的解題建議。
        5. 請不要使用 Latex，系統無法正確顯示。
        """
        self.agent = create_agent(
            model=self.model,
            system_prompt=self.system_prompt,
            middleware=[
                SummarizationMiddleware(
                    model=self.small_model,
                    max_tokens_before_summary= 2000,
                ),
                ContextEditingMiddleware(
                    edits=[
                        ClearToolUsesEdit(
                            trigger=2500,
                            keep=2,
                        ),
                    ],
                ),
            ],
            tools=[python_interpreter],
            checkpointer=self.checkpoint,
        )
    
class ExamPrepAgent(ChatAgent):
    def __init__(self, channel_id: int):
        super().__init__(channel_id=channel_id)
        self.system_prompt = self.base_system_prompt + """
        1. 現在是考試準備模式，協助學生準備即將到來的考試。
        2. 從學生提供的資訊中，提供有效的複習策略與重點整理。
        """
        self.agent = create_agent(
            model=self.model,
            system_prompt=self.system_prompt,
            middleware=[
                SummarizationMiddleware(
                    model=self.small_model,
                    max_tokens_before_summary= 2000,
                ),
                ContextEditingMiddleware(
                    edits=[
                        ClearToolUsesEdit(
                            trigger=2500,
                            keep=2,
                        ),
                    ],
                ),
            ],
            checkpointer=self.checkpoint
        )
