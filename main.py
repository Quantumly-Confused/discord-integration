import discord
import sys
from discord import app_commands
from dotenv import load_dotenv
import asyncio
import logging
from discord.ext import commands
from discord import File
import os
import io

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
intents.reactions = True
intents.members = True

load_dotenv()

class QCAdmin(commands.Cog):
    def __init__(self, bot):
        """Initializes the QCAdmin class with necessary setup for admin commands and cog management."""
        self.bot = bot
        self.logger = self.setup_logger()
        print("QCAdmin initialized")
        self.logger.info("QCAdmin initialized")

    def setup_logger(self):
        """Sets up logging for the bot."""
        logger = logging.getLogger("quantumly_confused_bot_log")
        logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler("quantumly_confused_bot.log", encoding="utf-8", mode="a")
        console_handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
        console_handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
        logger.addHandler(handler)
        logger.addHandler(console_handler)
        print(f"Log file created at: {handler.baseFilename}")
        return logger
    
    def add_logger_memory_handler(self):
        """Adds a memory handler to capture buffered log data."""
        # hold logs in memory and buffer up to 100 log records
        memory_handler = logging.handlers.MemoryHandler(capacity=100, target=None)
        memory_handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
        self.logger.addHandler(memory_handler)
        self.memory_handler = memory_handler

    @commands.Cog.listener()
    async def on_ready(self):
        """Event handler for when the bot is ready."""
        print(f"Logged in as {self.bot.user.name}")
        print(f"Discord.py API version: {discord.__version__}")
        print(f"Bot ID: {self.bot.user.id}")
        self.logger.info(f"Logged in as {self.bot.user.name} Discord.py API version: {discord.__version__} Bot ID: {self.bot.user.id}")

    def is_mod_or_admin():
        async def predicate(ctx):
            mod_role = discord.utils.get(ctx.guild.roles, name="Moderation Team")
            owner_role = discord.utils.get(ctx.guild.roles, name="Owner")
            admin_role = discord.utils.get(ctx.guild.roles, name="Admin")
            return mod_role in ctx.author.roles or admin_role in ctx.author.roles or owner_role in ctx.author.roles
        return commands.check(predicate)

    # Admin command group
    admin = app_commands.Group(name="admin", description="Admin commands for the bot.")
    
    @admin.command(name="sync", description="Syncs the bot's commands with Discord.")
    @is_mod_or_admin()
    async def sync_commands(self, Interaction: discord.Interaction):
        """ Syncs the bot's commands with Discord API."""
        await Interaction.response.defer()
        try:
            self.logger.info(f"Command sync initiated by {Interaction.user}...")
            synced = await self.bot.tree.sync()
            await Interaction.followup.send(f"Commands synced successfully! Synced {len(synced)} commands.")
            self.logger.info(f"Synced {len(synced)} commands.")
        except Exception as e:
            self.logger.error(f"Sync failed: {e}")
            await Interaction.followup.send(f"Sync failed: {e}")
            
    @admin.command(name="logbuffer", description="Command to capture logs from the log memory buffer.")
    async def memory_logbuffer(self, ctx):
        """Command to capture logs from the log memory buffer."""
        # Flush memory handler to the buffer 
        self.memory_handler.flush()  

        # Gather all log records from the buffer
        log_records = [self.memory_handler.format(record) for record in self.memory_handler.buffer]

        if not log_records:
            await ctx.send("No recent log entries found.")
            return

        # Combine log records but keep it under Discord's 2000 character limit
        log_data = "\n".join(log_records)
        if len(log_data) > 1900:
            log_data = log_data[-1900:]  # Trim to the last 1900 characters

        await ctx.send(f"```{log_data}```")

        # Clear method to clear the buffer
        self.memory_handler.buffer.clear()

    # Cog command group
    cog = app_commands.Group(name="cog", description="Manage bot cogs.")
    
    @cog.command(name="load", description="Loads a cog.")
    async def load_cog(self, Interaction: discord.Interaction, cog_name: str):
        await Interaction.response.defer()
        try:
            await self.bot.load_extension(cog_name)
            self.logger.info(f"Loaded {cog_name}")
            await Interaction.followup.send(f"Loaded {cog_name}")
        except Exception as e:
            self.logger.error(f"Failed to load {cog_name}: {e}")
            await Interaction.followup.send(f"Failed to load {cog_name}: {e}")

    @cog.command(name="unload", description="Unloads a cog.")
    async def unload_cog(self, Interaction: discord.Interaction, cog_name: str):
        await Interaction.response.defer()
        try:
            await self.bot.unload_extension(cog_name)
            self.logger.info(f"Unloaded {cog_name}")
            await Interaction.followup.send(f"Unloaded {cog_name}")
        except Exception as e:
            self.logger.error(f"Failed to unload {cog_name}: {e}")
            await Interaction.followup.send(f"Failed to unload {cog_name}: {e}")

    @cog.command(name="reload", description="Reloads a cog.")
    async def reload_cog(self, Interaction: discord.Interaction, cog_name: str):
        await Interaction.response.defer()
        try:
            await self.bot.reload_extension(cog_name)
            self.logger.info(f"Reloaded {cog_name}")
            await Interaction.followup.send(f"Reloaded {cog_name}")
        except Exception as e:
            self.logger.error(f"Failed to reload {cog_name}: {e}")
            await Interaction.followup.send(f"Failed to reload {cog_name}: {e}")

    @cog.command(name="loaded", description="Shows currently loaded extensions.")
    async def show_loaded_extensions(self, Interaction: discord.Interaction):
        loaded_extensions = list(self.bot.extensions)
        await Interaction.response.send_message(f"Currently loaded extensions: {loaded_extensions}")
        self.logger.info("Displayed loaded extensions")
        
    async def sync_commands(self):
        """Syncs the bot's commands with Discord on startup."""
        print("Bot Startup Command Sync initiated...")
        self.logger.info("Bot Startup Command Sync initiated...")
        try:
            synced = await self.bot.tree.sync()
            print(f"Command Sync Completed: Synced {len(synced)} commands.")
            self.logger.info(f"Command Sync Completed: Synced {len(synced)} commands.")
        except Exception as e:
            print(e)
            self.logger.error(f"Error syncing commands: {e}")

# Bot initialization and startup
async def main():
    bot = commands.Bot(command_prefix="/", intents=intents)
    qc_admin = QCAdmin(bot)
    bot.logger = qc_admin.logger
    await bot.start(os.getenv('DISCORD_API_TOKEN'))
    await bot.add_cog(qc_admin)
    await qc_admin.sync_commands()

if __name__ == '__main__':
    asyncio.run(main())
