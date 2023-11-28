import discord
from discord import app_commands
from dotenv import load_dotenv
import asyncio
import logging
from discord.ext import commands
import os
import io

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
intents.reactions = True
intents.members = True


#* Logging setup for the bot
logger = logging.getLogger("quantumly_confused_bot_log")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler("quantumly_confused_bot.log", encoding="utf-8", mode="a")
print(f"Log file created at: {handler.baseFilename}")
handler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
logger.addHandler(handler)

#* Load the .env to get the discord tokens
load_dotenv()

bot = commands.Bot(command_prefix="/", intents=intents)
bot.logger = logger



@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    print(f"Discord.py API version: {discord.__version__}")
    print(f"Bot ID: {bot.user.id}")
    print(f"Bot has loaded extensions: {bot.extensions}")
    print("------")
    logger.info(f"Logged in as {bot.user.name} Discord.py API version: {discord.__version__} Bot ID: {bot.user.id}")
    print(f"{bot} has connected to Discord.")
    logger.info(f"{bot} has connected to Discord.")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {synced} commands")
    except Exception as e:
        print(e)

async def load_cogs():
    """ Loads the cogs from the cogs folder"""
    print("Loading cogs...")
    cog_folders = ["grafana_discord_integration", "rcon_commands"]
    for cog_folder in cog_folders:
        full_path = f"./cogs/{cog_folder}"
        for filename in os.listdir(full_path):
            if filename.endswith(".py") and not filename.startswith("__init__"):
                extension = f"cogs.{cog_folder}.{filename[:-3]}"
                try:
                    await bot.load_extension(extension)
                    logger.info(f"Loaded {extension} successfully.")
                except Exception as e:
                    print(f"Failed to load {extension}, {e}")
                    logger.error(f"Failed to load {extension}, {e}")
    print("Finished loading cogs")

async def is_mod_or_admin():
    async def predicate(ctx):
        mod_role = discord.utils.get(ctx.guild.roles, name="Moderation Team")
        owner_role = discord.utils.get(ctx.guild.roles, name="Owner")
        admin_role = discord.utils.get(ctx.guild.roles, name="Admin")
        return mod_role in ctx.author.roles or admin_role in ctx.author.roles or owner_role in ctx.author.roles
    return commands.check(predicate)

class QCAdmin(commands.Cog):
    def __init__(self, bot):
        """ Initializes the QCAdmin class, which contains admin commands for the bot and cog management commands."""
        self.bot = bot
    
    # Create a group of commands for the interaction commands
    admin = app_commands.Group(name="admin", description="Admin commands for the bot.")
    
    @admin.command(name="sync", description="Syncs the bot's commands with Discord.")
    @is_mod_or_admin()
    async def sync_commands(self, Interaction: discord.Interaction):
        """ Syncs the bot's commands with Discord."""
        await Interaction.response.defer()
        try:
            logger.info(f"Command sync initiated by {Interaction.user}...")
            synced = await self.bot.tree.sync()
            await Interaction.followup.send(f"Commands synced successfully! Synced {len(synced)} commands.")
            logger.info(f"Synced {len(synced)} commands")
        except Exception as e:
            logger.error(f"Sync Failed. An error occurred: {e}")
            await Interaction.followup.send(f"Sync Failed. An error occurred: {e}")
            
    @admin.command(name="log", description="Gets or clears the bot's log file. Use 'get' or 'clear'.")
    @is_mod_or_admin()
    async def qc_log(Interaction: discord.Interaction, action: str = "get"):
        log_file_path = "quantumly_confused_bot.log"
        if action == "get":
            try:
                with open(log_file_path, "rb") as log_file:
                    log_content = log_file.read()
                    log_bytes = io.BytesIO(log_content)
                    log_attachment = File(fp=log_bytes, filename="quantumly_confused_bot.log")
                    await Interaction.response.send_message(file=log_attachment)
                    logger.info(f"The log file was retrieved by {Interaction.user}.")
            except FileNotFoundError:
                await Interaction.response.send_message(
                    "The log file could not be found.", ephemeral=True
                )
                logger.info("The log file could not be found.")

        elif action == "clear":
            try:
                open(log_file_path, "w").close()
                await Interaction.response.send_message(
                    f"The log file has been cleared by {Interaction.user}.", ephemeral=True
                )
                logger.info(f"The log file has been cleared by {Interaction.user}.")
            except Exception as e:
                await Interaction.response.send_message(
                    f"An error occurred: {str(e)}", ephemeral=True
                )
                logger.error(
                    f"An error occurred while trying to clear the log file: {str(e)}"
                )
        else:
            await Interaction.response.send_message(
                "Invalid action. Use 'get' or 'clear'.", ephemeral=True
            )
            logger.warning(
                f"Invalid action entered by {Interaction.user} for /admin log command."
            )

            
    cog = app_commands.Group(name="cog", description="Manage Bot Cogs.")
    @cog.command(name="load", description="Loads a cog.")
    async def load_cog(self, Interaction: discord.Interaction, cog_name: str):
        """ Loads a cog."""
        await Interaction.response.defer()
        try:
            extension = f"cogs.{cog_name}"
            await bot.load_extension(extension)
            logger.info(f"Loaded {extension}")
            await Interaction.followup.send(f"Loaded {extension}")
        except Exception as e:
            logger.info(f"Failed to load {cog_name}")
            await Interaction.followup.send(f"Failed to load {cog_name}")
            
    @cog.command(name="unload", description="Unloads a cog.")
    async def unload_cog(self, Interaction: discord.Interaction, cog_name: str):
        """ Unloads a cog."""
        await Interaction.response.defer()
        try:
            extension = f"cogs.{cog_name}"
            await bot.unload_extension(extension)
            await Interaction.followup.send(f"Unloaded {extension}")
        except Exception as e:
            print(f"Failed to unload {cog_name}")
            print(e)
            await Interaction.followup.send(f"Failed to unload {cog_name}")
            
    @cog.command(name="reload", description="Reloads a cog.") 
    async def reload_cog(self, Interaction: discord.Interaction, cog_name: str):
        """ Reloads a cog."""
        await Interaction.response.defer()
        try:
            extension = f"cogs.{cog_name}"
            await bot.reload_extension(extension)
            logger.info(f"Reloaded {extension}")
            await Interaction.followup.send(f"Reloaded {extension}")
        except Exception as e:
            print(f"Failed to reload {cog_name}")
            logger.error(f"Failed to reload {cog_name}")
            await Interaction.followup.send(f"Failed to reload {cog_name}")
            
    @cog.command(name="loaded", description="Shows currently loaded extensions.")
    async def show_loaded_extensions(self, Interaction: discord.Interaction):
        """ Shows currently loaded extensions."""
        loaded_extensions = list(bot.extensions)
        await Interaction.response.send_message(f"Currently loaded extensions: {loaded_extensions}")
        logger("Sent loaded extensions")

#* Bot setup steps and start
async def main():
    """ Main function for the bot."""
    await load_cogs()
    await bot.add_cog(QCAdmin(bot))
    await bot.start(os.getenv('DISCORD_API_TOKEN'))

if __name__ == '__main__':
    asyncio.run(main())