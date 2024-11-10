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

    @commands.Cog.listener()
    async def on_ready(self):
        """Event handler for when the bot is ready."""
        print(f"Logged in as {self.bot.user.name}")
        print(f"Discord.py API version: {discord.__version__}")
        print(f"Bot ID: {self.bot.user.id}")
        self.logger.info(f"Logged in as {self.bot.user.name} Discord.py API version: {discord.__version__} Bot ID: {self.bot.user.id}")
        try:
            synced = await self.bot.tree.sync()
            print(f"Synced {len(synced)} commands.")
            self.logger.info(f"Synced {len(synced)} commands.")
        except Exception as e:
            print(e)
            self.logger.error(f"Error syncing commands: {e}")

    async def load_cogs(self):
        """Loads the cogs from the cogs folder."""
        print("Loading cogs...")
        cog_folders = ["grafana_discord_integration", "rcon_commands", "qc_status", "quantum_pterodactyl"]
        self.logger.info(f"Loading cogs from {cog_folders}")
        for cog_folder in cog_folders:
            full_path = f"./cogs/{cog_folder}"
            if os.path.exists(full_path):
                for filename in os.listdir(full_path):
                    if filename.endswith(".py") and not filename.startswith("__init__"):
                        extension = f"cogs.{cog_folder}.{filename[:-3]}"
                        try:
                            await self.bot.load_extension(extension)
                            self.logger.info(f"Loaded {extension} successfully.")
                        except Exception as e:
                            print(f"Failed to load {extension}, {e}")
                            self.logger.error(f"Failed to load {extension}, {e}")
            else:
                print(f"Path {full_path} does not exist.")
                self.logger.warning(f"Path {full_path} does not exist")
        print("Finished loading cogs")
        self.logger.info("Finished loading cogs")

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
        await Interaction.response.defer()
        try:
            self.logger.info(f"Command sync initiated by {Interaction.user}...")
            synced = await self.bot.tree.sync()
            await Interaction.followup.send(f"Commands synced successfully! Synced {len(synced)} commands.")
            self.logger.info(f"Synced {len(synced)} commands.")
        except Exception as e:
            self.logger.error(f"Sync failed: {e}")
            await Interaction.followup.send(f"Sync failed: {e}")

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

# Bot initialization and startup
async def main():
    bot = commands.Bot(command_prefix="/", intents=intents)
    qc_admin = QCAdmin(bot)
    bot.logger = qc_admin.logger
    await bot.add_cog(qc_admin)
    await qc_admin.load_cogs()
    await bot.start(os.getenv('DISCORD_API_TOKEN'))

if __name__ == '__main__':
    asyncio.run(main())
