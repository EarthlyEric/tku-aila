import os
import logging
from discord.ext import commands
from discord import Intents
from discord.utils import _ColourFormatter

class Bot(commands.Bot):
    async def setup_hook(self):
        # Load Cogs
        await self.load_extension('cogs.debug')
        await self.load_extension('cogs.commands')
        await self.load_extension('cogs.conversations')
        # Sync Slash Commands to Discord
        await self.tree.sync()

# Set up bot with default intents
intents = Intents.default()
intents.message_content = True

bot = Bot(intents=intents, command_prefix="!?/")
# Remove default help command
bot.remove_command('help') 
# Set up logging
logger = logging.getLogger('tku-aila')
logger.setLevel(logging.INFO)
dt_fmt = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter('{asctime} [{levelname}] {name}: {message}', dt_fmt, style='{')
stream_formatter = _ColourFormatter()

if not os.path.exists('logs'):
    os.makedirs('logs')
logfile_handler = logging.FileHandler(filename='logs/bot.log', encoding='utf-8', mode='w')
logfile_handler.setFormatter(formatter)
logger.addHandler(logfile_handler)

log_handler = logging.StreamHandler()
log_handler.setFormatter(stream_formatter)
logger.addHandler(log_handler)

@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user}')
    
if __name__ == '__main__':
    # Load environment variables from .env file if it exists and run the bot.
    if os.path.exists('.env'):
        from dotenv import load_dotenv
        load_dotenv()
        if os.getenv("IS_DEVELOPMENT", "False").lower() == "true":
            logger.setLevel(logging.DEBUG)
            logger.debug("Running in development mode: Debug logging enabled.")
            

    token = os.getenv('DISCORD_TOKEN') 
    if not token:
        print("Error: Discord token not found in environment variables.")
    else:
        bot.run(token, log_handler=None, root_logger=True)  
    