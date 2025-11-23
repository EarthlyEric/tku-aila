import time
import discord
from discord.ext import commands
from discord import app_commands

THREAD_TYPES = (discord.ChannelType.public_thread, discord.ChannelType.private_thread)

class ConceptAI(commands.Cog):
    """ Simulated Response for conceptual AI interactions in Discord threads. """
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    def _get_mode_from_thread_name(self, thread_name: str) -> tuple[str, str | None]:
        """從討論串名稱解析出模式名稱和ID"""
        mode_map = { "修課規劃": "study", "課業輔導": "solve", "考試準備": "exam" }
        for name, mode_id in mode_map.items():
            if f"({name})" in thread_name:
                return name, mode_id
        return "未知模式", None
        
    @app_commands.command(name="start", description="啟動智慧學習助理")
    async def start_assistant(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        
        class AssistantSelect(discord.ui.Select):
            def __init__(self):
                options = [
                    discord.SelectOption(label="修課規劃與學分查詢 (畢業條件)", value="study"),
                    discord.SelectOption(label="課業輔導與疑難排解 (難題解析)", value="solve"),
                    discord.SelectOption(label="期中期末考試準備 (個人化複習)", value="exam"),
                ]
                super().__init__(placeholder="請選擇您需要的協助類型...", min_values=1, max_values=1, options=options)

            async def callback(self, select_interaction: discord.Interaction):
                choice = self.values[0]
                
                if choice == "study":
                    reply = "> 好的，針對【修課規劃】我們將啟動個人化輔導模組。\n專屬私人討論串已開啟..."
                    mode_welcome = "請輸入您的科系和年級，我可以為您檢查**必修學分**和**衝堂**狀況，並推薦下一學期最合適的課程組合。"
                    mode_name = "修課規劃"
                elif choice == "solve":
                    reply = "> 好的，針對【課業輔導】我們將啟動個人化輔導模組。\n專屬私人討論串已開啟..."
                    mode_welcome = "請貼上題目或描述問題，我會幫您分析與解題步驟。\n我會透過**步驟解析**和**相關例題**幫助您理解。"
                    mode_name = "課業輔導"
                elif choice == "exam":
                    reply = "> 好的，針對【考試準備】我們將啟動個人化輔導模組。\n專屬私人討論串已開啟..."
                    mode_welcome = "請說明您的考試科目及範圍，並說明偏好的學習形式（影片/文章/書籍），我會推薦資源並協助制定複習計畫。"
                    mode_name = "考試準備"
                else:
                    await select_interaction.response.send_message("發生錯誤：無效的選擇。", ephemeral=True)
                    return

                await select_interaction.response.send_message(reply, ephemeral=True)
                
                user = select_interaction.user
                thread_name = f"🤖 智慧學習助理  - {user.display_name} ({mode_name}) {time.strftime("%Y-%m-%d %H:%M:%S")}"

                try:

                    thread = await select_interaction.channel.create_thread(
                        name=thread_name,
                        auto_archive_duration=60, 
                        type=discord.ChannelType.private_thread,
                    )
                    await thread.add_user(user)
                    
                    thread_welcome = (
                        f"**💡 模式已啟動：【{mode_name}】**\n\n"
                        f"你好，{user.mention}！歡迎來到您的專屬輔導空間。\n"
                        f"這個討論串是私密的，只有您和我可以看到。\n\n"
                        f"**🎯 您的任務提示：**\n"
                        f"{mode_welcome}\n\n"
                        f"您可以隨時開始輸入您的問題或需求。"
                    )
                    
                    await thread.send(thread_welcome)
                    
                    await select_interaction.followup.send(
                        f"您的專屬學習助理已在 {thread.mention} 中啟動！請點擊進入開始對話。",
                        ephemeral=True
                    )
                    
                except discord.Forbidden:
                    await select_interaction.followup.send(
                        "發生權限錯誤：我無法在這個頻道中建立私人討論串或邀請您進入。請檢查我的權限設定。", 
                        ephemeral=True
                    )
                except Exception as e:
                    await select_interaction.followup.send(
                        f"啟動助理時發生未知錯誤: {e}", 
                        ephemeral=True
                    )

        class AssistantView(discord.ui.View):
            def __init__(self, timeout: float = 180):
                super().__init__(timeout=timeout)
                self.add_item(AssistantSelect())

        view = AssistantView()
        welcome_message = """
        # 歡迎您！我是您的 AI 智慧學習顧問。
        > 為了提供最個人化的學習建議，請問您目前最需要的協助是什麼呢?
        > 請從下面選擇您需要的協助：
        """

        await interaction.followup.send(welcome_message, view=view, ephemeral=True)
        
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):

        if message.author == self.bot.user:
            return

        if message.channel.type not in THREAD_TYPES:
            return

        thread_name = message.channel.name
        if not thread_name.startswith("🤖 智慧學習助理"):
            return
            
        user_message = message.content.strip()
        if not user_message:
            return

        mode_id = self._get_mode_from_thread_name(thread_name)
    
        await message.channel.typing()
            
        if mode_id:
            content = message.content.lower()
            default_response = "收到您的問題。我已將其與您的學習地圖進行匹配，並為您推送相關的**知識點講解微影片**。請問還有其他學習上的疑問嗎？"
            response = default_response

            if mode_id == "study":
                if "選課" in content or "畢業學分" in content:
                    response = (
                        "請注意，您的系上必修【線性代數】必須先修完【微積分】，否則將無法在下學期選課成功。我已將此規則標註在您的課程規劃中。"
                    )
            elif mode_id == "solve":
                if "微積分" in content or "極限" in content:
                    response = (
                    "微積分中的**極限概念**通常是難點。我們可以從**$\\epsilon-\\delta$定義**的視覺化解釋開始，"
                    "並提供三道相關練習題來加深您的理解。"
                    )

            elif mode_id == "exam":
                if "挫折" in content or "看不懂" in content:
                    response = (
                        "我理解您可能感到有點受挫。沒關係，學習本來就是循序漸進的。AI已自動為您調整內容難度，"
                        "我們將改用**更生活化的例子**來解釋這個概念，讓您輕鬆一點！"
                    )
                    
        await message.channel.send(response)

async def setup(bot: commands.Bot):
    await bot.add_cog(ConceptAI(bot))