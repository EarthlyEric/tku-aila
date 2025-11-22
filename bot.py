import os
from discord.ext import commands
from discord import Intents
from discord.utils import logging

class Bot(commands.Bot):
    async def setup_hook(self):
        # Load Cogs
        await self.load_extension('cogs.debug')
        await self.load_extension('cogs.fake_ai')
        # Sync Slash Commands to Discord
        await self.tree.sync()

# Set up bot with default intents
intents = Intents.default()
intents.message_content = True

bot = Bot(intents=intents)
# Remove default help command
bot.remove_command('help') 
# Set up logging
logger = logging.getLogger('discord')

@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user}')

if __name__ == '__main__':
    # Load environment variables from .env file if it exists and run the bot.
    if os.path.exists('.env'):
        from dotenv import load_dotenv
        load_dotenv()

    token = os.getenv('discord_token') 
    if not token:
        print("Error: Discord token not found in environment variables.")
    else:
        bot.run(token)
    