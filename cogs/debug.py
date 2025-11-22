from discord.ext import commands

class Debug(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="ping", description="Check bot latency", with_app_command=True)
    async def ping(self, ctx: commands.Context):
        latency = self.bot.latency * 1000
        await ctx.send(f"Pong! Latency: {latency:.2f} ms")
        
    @commands.hybrid_command(name="reload",description="Reload a certain cog !", with_app_command=True)
    @commands.is_owner()
    async def reload(self, ctx:commands.Context, extension:str):
        try:
            if extension == "debug":
                # Bro, you can't reload the debug cog while using it :)
                return await ctx.send("Cannot reload the debug cog while it's in use. Please restart the bot to apply changes.")
            await self.bot.reload_extension(f'cogs.{extension}')
            await self.bot.tree.sync()
            await ctx.send(f"Reloaded cog: {extension}")
        except Exception as e:
            await ctx.send(f"Failed to reload cog: {extension}\nError: {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(Debug(bot))