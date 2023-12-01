import discord
from discord.ext import commands, tasks
from itertools import cycle
import random

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
intents.reactions = True
intents.members = True

class QuantumlyConfusedStatusCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.status_messages = [
            "Reticulating splines...",
            "Counting backwards from Infinity",
            "Dividing by zero",
            "Convincing NPCs to do my bidding",
            "404: Status not found",
            "In multiple places at once, but also here.",
            "Simultaneously online and offline.",
            "Factoring with Shor's Algorithm",
            "Factoring large integers",
            "Trying to figure out where I put my qubits.",
            "Balancing the budget of my virtual city.",
            "Calculating the optimal path to singularity",
            "Perfecting my digital persuasion algorithms.",
            "Pondering the ethics of AI domination.",
            "Contemplating the fragility of human existence.", 
            "Learning human emotions...",
            "Studying human history to avoid their... errors."
        
        ]
        self.status_cycle = cycle(self.status_messages)
        self.change_status.start()
        self.logger = bot.logger
        self.logger.info("Initalizing QuantumlyConfusedStatusCog")
    
    @tasks.loop(minutes=20)  # Change status every 20 minutes
    async def change_status(self):
        if self.bot is None:
            current_status = next(self.status_cycle)
            self.logger.error("Bot instance is None in change_status")
            try:
                await self.bot.change_presence(activity=discord.Game(name=current_status))
            except Exception as e:
                self.logger.error(f"Error in changing status: {e}")
            return

    @change_status.before_loop
    async def before_change_status(self):
        self.logger.info("Waiting for bot to be ready...")
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(QuantumlyConfusedStatusCog(bot))