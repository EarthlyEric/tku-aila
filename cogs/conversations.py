import discord
import logging
from discord.ext import commands
from lib.ai import SchedulerAI

logger = logging.getLogger('tku-aila')

class ConversationsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            logger.debug('Ignoring message from bot user')
            return

        if not isinstance(message.channel, discord.Thread):
            logger.debug('Message not in a thread: channel=%s type=%s', message.channel, type(message.channel))
            return

        thread_name = getattr(message.channel, 'name', '')
        if not thread_name or not thread_name.startswith("AI 學習助理"):
            logger.debug('Thread name does not match: %s', thread_name)
            return
        
        user_message = message.content.strip()
        if not user_message:
            return
        
        async with message.channel.typing():
            try:
                ai = SchedulerAI() # Currently only SchedulerAI is implemented
                response_structure = ai.agent.invoke(input=ai.user_input(user_message))
            except Exception as e:
                logger.exception('AI invocation failed')
                await message.channel.send("抱歉，內部服務發生錯誤，請稍後再試。")
                return

            messages = response_structure.get('messages', []) if isinstance(response_structure, dict) else []
            if messages:
                parsed_response = messages[-1].content
                await message.channel.send(parsed_response)
            else:
                # Classic fallback response :)
                await message.channel.send("抱歉，我無法處理您的請求。請稍後再試。 :(")
        
async def setup(bot: commands.Bot):
    await bot.add_cog(ConversationsCog(bot))