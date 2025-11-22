import discord
from discord.ext import commands
from discord import app_commands

class CommandsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    @app_commands.command(name="hello", description="啟動 AI 智慧學習助理")
    async def hello(self, interaction: discord.Interaction):
        """啟動 AI 智慧學習助理，並提供個人化學習建議選項。"""
        await interaction.response.defer(ephemeral=True)

        class AssistantSelect(discord.ui.Select):
            def __init__(self):
                options = [
                    discord.SelectOption(label="修課規劃", description="根據您的學習地圖提供選課與學習策略建議", value="schedule"),
                    discord.SelectOption(label="問題解決", description="協助您解決學習中的具體問題與疑惑", value="solve"),
                    discord.SelectOption(label="考試準備", description="提供考前複習計劃與重點整理建議", value="exam"),
                ]
                super().__init__(placeholder="請選擇您需要的協助類型", min_values=1, max_values=1, options=options)

            async def callback(self, interaction: discord.Interaction):
                mode = self.values[0]
                thread = await interaction.channel.create_thread(
                    name=f"AI 智慧學習助理 - {mode}",
                    type=discord.ChannelType.private_thread,
                    reason="User initiated AI learning assistant thread"
                )
                await thread.add_user(interaction.user)
                await thread.send(f"您好！這是您的智慧學習助理私人討論區，您選擇的協助類型是：**{mode}**。請在此提出您的問題或需求，我將竭誠為您服務！")
                await interaction.followup.send(f"已為您建立專屬討論串：{thread.mention}，請點擊進入討論。", ephemeral=True)

        class AssistantView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=180)
                self.add_item(AssistantSelect())

        view = AssistantView()
        welcome_message = """
        # 歡迎您！我是您的 AI 智慧學習顧問。
        > 為了提供最個人化的學習建議，請問您目前最需要的協助是什麼呢?
        > 請從下面選擇您需要的協助：
        """

        await interaction.followup.send(welcome_message, view=view, ephemeral=True)