import discord
from discord.ext import commands
from discord import app_commands

class Debug(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Check bot latency")
    async def ping(self, interaction: discord.Interaction):
        latency = self.bot.latency * 1000
        await interaction.response.send_message(f"Pong! Latency: {latency:.2f} ms", ephemeral=True)
        
    @app_commands.command(name="reload",description="Reload a certain cog !")
    @commands.is_owner()
    async def reload(self, interaction: discord.Interaction, extension:str):
        try:
            if extension == "debug":
                # Bro, you can't reload the debug cog while using it :)
                return await interaction.response.send_message("Cannot reload the debug cog while it's in use. Please restart the bot to apply changes.", ephemeral=True)
            await self.bot.reload_extension(f'cogs.{extension}')
            await self.bot.tree.sync()
            await interaction.response.send_message(f"Reloaded cog: {extension}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Failed to reload cog: {extension}\nError: {e}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Debug(bot))