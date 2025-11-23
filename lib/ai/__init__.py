from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain.messages import HumanMessage

class Agent:
    model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0, max_output_tokens=1024, max_retries=2)
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
        )
    
class SolverAgent(Agent):
    def __init__(self, channel_id: int):
        super().__init__(channel_id=channel_id)
        self.system_prompt = self.base_system_prompt + " You are a problem-solving assistant." # Placeholder prompt
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
