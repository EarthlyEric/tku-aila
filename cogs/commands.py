import time
import asyncio
import discord
from discord.ext import commands
from discord import app_commands

class CommandsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    @app_commands.command(name="start", description="啟動 AI 智慧學習助理")
    async def start(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        class AssistantSelect(discord.ui.Select):
            def __init__(self):
                options = [
                    discord.SelectOption(label="修課規劃", description="根據您的學習地圖提供選課與學習策略建議", value="schedule"),
                    discord.SelectOption(label="難題解決", description="協助您解決學習中的具體問題與疑惑", value="solve"),
                    discord.SelectOption(label="考試準備", description="提供考前複習計劃與重點整理建議", value="exam"),
                ]
                super().__init__(placeholder="請選擇您需要的協助類型", min_values=1, max_values=1, options=options)

            async def callback(self, interaction: discord.Interaction):
                mode = self.values[0]
                mode_map = {
                    "schedule": "修課規劃",
                    "solve": "難題解決",
                    "exam": "考試準備"
                }
                await interaction.response.defer(ephemeral=True)
                thread = await interaction.channel.create_thread(
                    name=f"AI 學習助理 - {mode_map[mode]} - {interaction.user.name} - {time.strftime('%Y%m%d-%H%M%S')}",
                    type=discord.ChannelType.private_thread,
                    reason="User initiated AI learning assistant thread",
                    auto_archive_duration=1440
                )
                await thread.add_user(interaction.user)
                thread_welcome = (
                        f"**💡 模式已啟動：【{mode}】**\n\n"
                        f"你好，{interaction.user.mention}！歡迎來到您的專屬輔導空間。\n"
                        f"這個討論串是私密的，只有您和我可以看到。\n\n"
                        f"您可以隨時開始輸入您的問題或需求。"
                    )
                await thread.send(thread_welcome)
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
        
        
    @app_commands.command(name="close", description="關閉當前的 AI 智慧學習助理討論串")
    async def close(self, interaction: discord.Interaction):
        if interaction.channel.type in [discord.ChannelType.private_thread, discord.ChannelType.public_thread]:
            await interaction.response.send_message("討論串即將被關閉。 倒數5秒...", ephemeral=True)
            
            await asyncio.sleep(5)
            await interaction.channel.delete()
        else:
            await interaction.response.send_message("此指令只能在討論串中使用。", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(CommandsCog(bot))