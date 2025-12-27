import os
import sys
import time
import logging
from discord.ext import commands
from discord import Intents
from discord.utils import _ColourFormatter
from tools.db import DBInitializer, DBSessionManager
from tools.db.models import Metadata
from tools.acad import ACADDownloader, ACADProcessor

# Load environment variables from .env file if it exists
if os.path.exists('.env'):
    from dotenv import load_dotenv
    load_dotenv()

class Bot(commands.Bot):
    async def setup_hook(self):
        # Load Cogs
        if os.getenv("IS_DEVELOPMENT", "False").lower() == "true":
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
        "COURSES_DATABASE_PATH",
        "REDIS_URL"
    ]
        
    for env in envs:
        if os.getenv(env) is None:
            logger.error(f"{env} not found in environment variables.")
            sys.exit(1)
            
        if env == "REDIS_URL":
            import redis
            redis_client = redis.Redis.from_url(os.getenv("REDIS_URL"))
            try:
                redis_client.ping()
                logger.info("Redis ping successful.")
            except Exception as e:
                logger.error(f"Redis ping failed: {e}")
                logger.error("Exiting due to Redis connection failure.")
                sys.exit(1)
                
    logger.info("Initializing database...")
    try:
        db_init = DBInitializer()
        db_init.init_db()
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        sys.exit(1)

    sync_manager = DBSessionManager()
    current_year = None
    current_semester = None

    try:
        with sync_manager.get_session() as session:
            meta = session.get(Metadata, 1)
            if meta:
                current_year = meta.year
                current_semester = meta.semester
                logger.info("Local database version: %s-%s", current_year, current_semester)
            else:
                logger.info("Local database is empty.")
    except Exception as e:
        logger.error(f"Failed to query database metadata: {e}")
        logger.info("Proceeding with fresh database download...")

    downloader = ACADDownloader()

    check_year = str(current_year) if current_year is not None else "-1"
    check_semester = str(current_semester) if current_semester is not None else "-1"

    try:
        if downloader.has_update(check_year, check_semester):
            logger.info("New version found or database empty. Downloading...")

            file_data = downloader.download_file()

            processor = ACADProcessor()
            contents = processor.unpack_file(file_data['file_bytes']) 
            processor.generate_database(contents, file_data['metadata'])
        else:
            logger.info("Database is up to date. No action taken.")
    except Exception as e:
        logger.error(f"Failed to download or process course data: {e}")
        if current_year is None:
            logger.error("No local database available and download failed. Exiting.")
            sys.exit(1)
        else:
            logger.warning("Using existing local database.")
    
    token = os.getenv('DISCORD_TOKEN') 
    bot.run(token, log_handler=None)  
    