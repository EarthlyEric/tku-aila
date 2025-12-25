import os
import sys
import time
import logging
from discord.ext import commands
from discord import Intents
from discord.utils import _ColourFormatter

# Load environment variables from .env file if it exists
if os.path.exists('.env'):
    from dotenv import load_dotenv
    load_dotenv()

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
logfile_handler = logging.FileHandler(filename=f'logs/bot-{time.strftime("%Y%m%d-%H%M%S")}.log', encoding='utf-8', mode='w')
logfile_handler.setFormatter(formatter)
logger.addHandler(logfile_handler)

log_handler = logging.StreamHandler()
log_handler.setFormatter(stream_formatter)
logger.addHandler(log_handler)

@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user}')
    
if __name__ == '__main__':
    # Check for required environment variables
    if os.getenv("IS_DEVELOPMENT", "False").lower() == "true":
        logger.setLevel(logging.DEBUG)
        logger.debug("Running in development mode: Debug logging enabled.")
        
    envs = [
        "DISCORD_TOKEN",
        "CF_AI_GATEWAY_TOKEN",
        "CF_ACCOUNT_ID",
        "CF_GATEWAY_ID",
        "MODEL_NAME",
        "SMALL_MODEL_NAME",
        "REDIS_URL"
    ]
        
    for env in envs:
        if os.getenv(env) is None:
            logger.error(f"{env} not found in environment variables.")
            sys.exit(1)
            
        if env == "REDIS_URL":
            from lib.checker import Checker
            checker = Checker(redis_url=os.getenv("REDIS_URL"))
            if not checker.redis_is_available():
                logger.error("Redis service is not available. Exiting.")
                sys.exit(1)

    token = os.getenv('DISCORD_TOKEN') 
    bot.run(token, log_handler=None)  
    