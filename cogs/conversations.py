import discord
import logging
from discord.ext import commands
from ai.agents import SchedulerAgent, SolverAgent, ExamPrepAgent

logger = logging.getLogger('tku-aila')

class ConversationsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    def get_model_from_thread_name(self, thread_name: str ,channel_id: int) -> SchedulerAgent | SolverAgent | ExamPrepAgent | None:
        if "修課規劃" in thread_name:
            return SchedulerAgent(channel_id=channel_id)
        elif "難題解決" in thread_name:
            return SolverAgent(channel_id=channel_id)
        elif "考試準備" in thread_name:
            return ExamPrepAgent(channel_id=channel_id)
        return None
        
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
                ai = self.get_model_from_thread_name(thread_name, channel_id=message.channel.id)
                if hasattr(ai, 'checkpoint') and hasattr(ai.checkpoint, 'setup'):
                    await ai.checkpoint.setup()
                    
                if ai is None:
                    logger.debug('Get mode failed for thread: %s', thread_name)
                    return
                response = await ai.agent.ainvoke(input=ai.user_input(user_message), config={"configurable": {"thread_id": str(message.channel.id)}})
            except Exception as e:
                logger.exception('AI invocation failed')
                await message.channel.send("抱歉，內部服務發生錯誤，請稍後再試。")
                return

            message_content = ai.parse_response(response)
            
            if len(message_content) > 2000:
                chunks = [message_content[i:i+2000] for i in range(0, len(message_content), 2000)]
                for chunk in chunks:
                    await message.channel.send(chunk)
                    return
            else:
                await message.channel.send(message_content)
                return
        
async def setup(bot: commands.Bot):
    await bot.add_cog(ConversationsCog(bot))