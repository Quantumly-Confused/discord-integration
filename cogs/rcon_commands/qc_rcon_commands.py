import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import asyncio
import os
import time
from discord.ext.commands import has_permissions
from typing import Optional
from mcrcon import MCRcon

# * Define the intents for the bot (this is required for the discord-py-slash-commands library))
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
intents.reactions = True
intents.members = True

# * Load the .env to get the rcon server details
load_dotenv()

rcon_host = str(os.getenv("RCON_HOST"))
rcon_password = str(os.getenv("RCON_PASSWORD"))
rcon_port = int(os.getenv("RCON_PORT"))

# section Code defining the Cog and its attributes/functions


class Quantum_RCON_Commands_Cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = bot.logger

    # discord - rcon command group for use with the discord-py-slash-commands library, this will group the rcon related commands beneath /rcon.
    # discord - due to the number of commands, the rcon command group is further split into subgroups for better organisation. (world, )
    rcon = app_commands.Group(
        name="rcon", description="Send RCON commands to the Minecraft Server."
    )

    @rcon.command(
        name="say",
        description="Send a message from the Bot to the server. Usage <message>",
    )
    async def say(self, *thing_to_say: str):
        """Send a message from the Bot to the server. Usage <message>"""
        command = f"say {thing_to_say}"
        with MCRcon(rcon_host, rcon_password, port=rcon_port) as mcr:
            response = mcr.command(command)
            self.logger.info(f"Bot said {thing_to_say} in the server chat.")

    @rcon.command(name="status", description="Check the server status.")
    async def status(self, Interaction: discord.Interaction):
        """Check the server status."""
        try:
            start_time = time.time()
            command = f"status"
            with MCRcon(rcon_host, rcon_password, port=rcon_port) as mcr:
                response = mcr.command(command)
                end_time = time.time()
            # get the ping of the server, start time - end time * 1000 to get the latency in ms
            latency = round((end_time - start_time) * 1000)
            await Interaction.response.send_message(
                f"Server Status: {response}\nLatency: {latency}ms"
            )
            self.logger.info(f"Server Status: {response}\nLatency: {latency}ms")
        except Exception as e:
            await Interaction.response.send_message(
                f"Failed to retrieve server status: {e}"
            )
            self.logger.error(f"Failed to retrieve server status: {e}")

    @rcon.command(
        name="weather",
        description="Change the weather. Usage <weather_type> \n Valid weather types: clear, rain, thunder",
    )
    @has_permissions(manage_channels=True)
    async def weather(self, Interaction: discord.Interaction, weather_type: str):
        """Change the weather. Usage <weather_type> \n Valid weather types: clear, rain, thunder"""
        valid_types = ["clear", "rain", "thunder"]
        if weather_type.lower() not in valid_types:
            await Interaction.response.send_message(
                "Invalid weather type. Choose from clear, rain, or thunder."
            )
            self.logger.warning(
                f"{Interaction.user} attempted to set an Invalid weather type: {weather_type}"
            )
            return
        command = f"/weather {weather_type}"
        with MCRcon(rcon_host, rcon_password, port=rcon_port) as mcr:
            response = mcr.command(command)
            await Interaction.response.send_message(
                f"Weather changed to {weather_type}."
            )
            self.logger.info(f"{Interaction.user} changed Weather to {weather_type}.")

    @rcon.command(
        name="ablity",
        description="Set a player's ability value. Usage <player> <ability> <value>",
    )
    @has_permissions(manage_channels=True)
    async def ability(
        self, Interaction: discord.Interaction, player: str, ability: str, value: int
    ):
        """Set a player's ability value. Usage <player> <ability> <value>"""
        command = f"{player} {ability} {value}"
        with MCRcon(rcon_host, rcon_password, port=rcon_port) as mcr:
            response = mcr.command(command)
            await Interaction.response.send_message(
                f"{player} ability: {ability} set to {value}."
            )
            self.logger.info(
                f"{Interaction.user} set {player} ability: {ability} to {value}."
            )

    @rcon.command(
        name="advancement",
        description="Grant or revoke advancements to players. Usage <player> <action> <advancement>",
    )
    @has_permissions(manage_channels=True)
    async def advancement(
        self,
        Interaction: discord.Interaction,
        player: str,
        action: str,
        advancement: str,
    ):
        """Grant or revoke advancements to players. Usage <player> <action> <advancement>"""
        command = f"{player} {action} {advancement}"
        with MCRcon(rcon_host, rcon_password, port=rcon_port) as mcr:
            response = mcr.command(command)
            await Interaction.response.send_message(
                f"{player} was {action} {advancement}."
            )
            self.logger.info(f"{Interaction.user} {player} {action} {advancement}.")

    @rcon.command(
        name="ban", description="Ban a player from the server. Usage <player>"
    )
    @has_permissions(manage_channels=True)
    async def ban(self, Interaction: discord.Interaction, player: str):
        """Ban a player from the server. Usage <player>"""
        command = f"ban {player}"
        with MCRcon(rcon_host, rcon_password, port=rcon_port) as mcr:
            response = mcr.command(command)
            await Interaction.response.send_message(
                f"{player} has been banned from the server."
            )
            self.logger.info(f"{Interaction.user} banned {player}.")

    @rcon.command(
        name="ban-ip", description="Ban an IP address from the server. Usage <ip>"
    )
    @has_permissions(manage_channels=True)
    async def ban_ip(self, Interaction: discord.Interaction, ip: str):
        """Ban an IP address from the server. Usage <ip>"""
        command = f"ban-ip {ip}"
        with MCRcon(rcon_host, rcon_password, port=rcon_port) as mcr:
            response = mcr.command(command)
            await Interaction.response.send_message(
                f"{ip} has been banned from the server."
            )
            self.logger.info(f"{Interaction.user} IP banned {ip}.")

    @rcon.command(name="banlist", description="List all banned players.")
    @has_permissions(manage_channels=True)
    async def banlist(self, Interaction: discord.Interaction):
        """List all banned players."""
        command = "banlist"
        with MCRcon(rcon_host, rcon_password, port=rcon_port) as mcr:
            response = mcr.command(command)
            if response:
                await Interaction.response.send_message(f"Banned players: {response}")
            else:
                await Interaction.response.send_message("No players are banned.")
            self.logger.info(f"{Interaction.user} listed banned players.")

    @rcon.command(
        name="clear",
        description="Clear items from a player's inventory. Usage <player> [item] [count]",
    )
    @has_permissions(manage_channels=True)
    async def clear(
        self,
        Interaction: discord.Interaction,
        player: str,
        item: str = None,
        count: int = None,
    ):
        """Clear items from a player's inventory. Usage <player> [item] [count]"""
        command = (
            f"clear {player} {item if item else ''} {count if count else ''}".strip()
        )
        with MCRcon(rcon_host, rcon_password, port=rcon_port) as mcr:
            response = mcr.command(command)
            await Interaction.response.send_message(
                f"Cleared items from {player}'s inventory."
            )
            self.logger.info(
                f"{Interaction.user} Cleared items from {player} inventory."
            )

    @rcon.command(
        name="clone",
        description="Clone blocks. Usage <start_pos> <end_pos> <destination> [mask_mode] [clone_mode] [tile_mode]",
    )
    @has_permissions(manage_channels=True)
    async def clone(
        self,
        Interaction: discord.Interaction,
        start_pos: int,
        end_pos: int,
        destination: int,
        mask_mode: bool = None,
        clone_mode: bool = None,
        tile_mode: bool = None,
    ):
        """Clone blocks. Usage <start_pos> <end_pos> <destination> [mask_mode] [clone_mode] [tile_mode]"""
        command = f"clone {start_pos} {end_pos} {destination} {mask_mode if mask_mode else ''} {clone_mode if clone_mode else ''} {tile_mode if tile_mode else ''}".strip()
        with MCRcon(rcon_host, rcon_password, port=rcon_port) as mcr:
            response = mcr.command(command)
        await Interaction.response.send_message(
            f"Blocks cloned from {start_pos} to {end_pos} to {destination}."
            + (f" with mask mode {mask_mode}" if mask_mode else "")
            + (f", clone mode {clone_mode}" if clone_mode else "")
            + (f", tile mode {tile_mode}" if tile_mode else "")
            + "."
        )

    @rcon.command(
        name="damage", description="Damage entities. Usage <entities> <amount>"
    )
    async def damage(
        self, Interaction: discord.Interaction, entities: str, amount: int
    ):
        """Damage entities. Usage <entities> <amount>"""
        command = f"damage {entities} {amount}"
        with MCRcon(rcon_host, rcon_password, port=rcon_port) as mcr:
            response = mcr.command(command)
        await Interaction.response.send_message(f"Damaged {entities} by {amount}.")

    @rcon.command(
        name="daylock",
        description="Lock or unlock the day-night cycle. Alias: alwaysday. Usage <action>",
    )
    @has_permissions(manage_channels=True)
    async def daylock(self, Interaction: discord.Interaction, action: str):
        """Lock or unlock the day-night cycle. Alias: alwaysday. Usage <action>"""
        command = f"daylock {action}"
        with MCRcon(rcon_host, rcon_password, port=rcon_port) as mcr:
            response = mcr.command(command)
        await Interaction.response.send_message(f"Daylock {action}.")

    @rcon.command(
        name="difficulty", description="Change the game difficulty. Usage <level>"
    )
    @has_permissions(manage_channels=True)
    async def difficulty(self, Interaction: discord.Interaction, level: int):
        """Change the game difficulty. Usage <level>"""
        command = f"difficulty {level}"
        with MCRcon(rcon_host, rcon_password, port=rcon_port) as mcr:
            response = mcr.command(command)
            await Interaction.response.send_message(f"Game difficulty set to {level}.")

    @rcon.command(
        name="gamerule",
        description="Set or query a game rule value. Usage <rule> [value]",
    )
    @has_permissions(manage_channels=True)
    async def gamerule(
        self, Interaction: discord.Interaction, rule: str, value: str = None
    ):
        """Set or query a game rule value. Usage <rule> [value]"""
        command = f"gamerule {rule} {value if value else ''}".strip()
        with MCRcon(rcon_host, rcon_password, port=rcon_port) as mcr:
            response = mcr.command(command)
        await Interaction.response.send_message(
            f"Game rule {rule} set to {value}."
            if value
            else f"Game rule {rule} is {response}."
        )

    @rcon.command(
        name="effect",
        description="Give an effect to a player or entity. Usage <target> <effect> [duration] [amplifier]",
    )
    @has_permissions(manage_channels=True)
    async def effect(
        self,
        Interaction: discord.Interaction,
        target: str,
        effect: str,
        duration: int = None,
        amplifier: str = None,
    ):
        """Give an effect to a player or entity. Usage <target> <effect> [duration] [amplifier]"""
        command = f"effect give {target} {effect} {duration if duration else ''} {amplifier if amplifier else ''}".strip()
        with MCRcon(rcon_host, rcon_password, port=rcon_port) as mcr:
            response = mcr.command(command)
            await Interaction.response.send_message(
                f"Effect {effect} given to {target}."
            )

    @rcon.command(
        name="enchantment",
        description="Enchant a player item. Usage <player> <enchantment> [level]",
    )
    @has_permissions(manage_channels=True)
    async def enchant(
        self,
        Interaction: discord.Interaction,
        player: str,
        enchantment: str,
        level: int = None,
    ):
        """Enchant a player item. Usage <player> <enchantment> [level]"""
        command = f"enchant {player} {enchantment} {level if level else ''}".strip()
        with MCRcon(rcon_host, rcon_password, port=rcon_port) as mcr:
            response = mcr.command(command)
            await Interaction.response.send_message(
                f"Enchantment {enchantment} applied to {player}."
            )

    # discord - creation of world command group .
    world = app_commands.Group(
        name="world",
        description="Send RCON commands to the Minecraft Server - Manage World Attributes.",
    )

    @world.command(
        name="fill",
        description="Fill a region with a specific block. Usage <start_pos> <end_pos> <block> [mode]",
    )
    async def fill(
        self,
        Interaction: discord.Interaction,
        start_pos: int,
        end_pos: int,
        block: str,
        mode: str = None,
    ):
        """Fill a region with a specific block. Usage <start_pos> <end_pos> <block> [mode]"""
        command = f"fill {start_pos} {end_pos} {block} {mode if mode else ''}".strip()
        async with MCRcon(rcon_host, rcon_password, port=rcon_port) as mcr:
            response = mcr.command(command)
            await Interaction.response.send_message(
                f"Filled region from {start_pos} to {end_pos} with {block}."
                + (f" in mode {mode}" if mode else "")
                + "."
            )

    @world.command(
        name="fillbiome",
        description="Fill a region with a specific biome. Usage <start_pos> <end_pos> <biome>",
    )
    @has_permissions(manage_channels=True)
    async def fillbiome(
        self, Interaction: discord.Interaction, start_pos: int, end_pos: int, biome: str
    ):
        """Fill a region with a specific biome. Usage <start_pos> <end_pos> <biome>"""
        command = f"fillbiome {start_pos} {end_pos} {biome}"
        async with MCRcon(rcon_host, rcon_password, port=rcon_port) as mcr:
            response = mcr.command(command)
            await Interaction.response.send_message(
                f"Filled region from {start_pos} to {end_pos} with {biome}."
            )

    @rcon.command(
        name="give",
        description="Give items to a player. Usage <player> <item> <amount>",
    )
    @has_permissions(manage_channels=True)
    async def give(
        self, Interaction: discord.Interaction, player: str, item: str, amount: int
    ):
        """Give items to a player. Usage <player> <item> <amount>"""
        command = f"give {player} {item} {amount}"
        with MCRcon(rcon_host, rcon_password, port=rcon_port) as mcr:
            response = mcr.command(command)
            await Interaction.response.send_message(
                f"Gave {amount} of {item} to {player}."
            )

    @rcon.command(
        name="kick",
        description="Kick a player from the server. Usage <player> [reason]",
    )
    @has_permissions(manage_channels=True)
    async def kick(
        self, Interaction: discord.Interaction, player: str, *, reason: str = None
    ):
        """Kick a player from the server. Usage <player> [reason]"""
        command = f"kick {player} {reason}" if reason else f"kick {player}"
        with MCRcon(rcon_host, rcon_password, port=rcon_port) as mcr:
            response = mcr.command(command)
            await Interaction.response.send_message(
                f"{player} has been kicked from the server. Reason: {reason}"
                if reason
                else f"{player} has been kicked from the server."
            )

    # todo complete this function
    # Function for the /kill command
    def kill(entities):
        pass

    @rcon.command(name="listplayers", description="List all players on the server.")
    @has_permissions(manage_channels=True)
    async def list_players(self, Interaction: discord.Interaction):
        """List all players on the server."""
        command = "list"
        with MCRcon(
            rcon_host, rcon_password, port=int(rcon_port)
        ) as mcr:  # Ensure port is an integer
            response = mcr.command(command)
            await Interaction.response.send_message(
                f"Denizens on the server: {response}"
            )

    @rcon.command(
        name="op", description="Grant operator status to a player. Usage <player>"
    )
    @has_permissions(manage_channels=True)
    async def op(self, Interaction: discord.Interaction, player: str):
        """Grant operator status to a player. Usage <player>"""
        command = "op"
        async with MCRcon(
            rcon_host, rcon_password, port=int(rcon_port)
        ) as mcr:  # Ensure port is an integer
            response = mcr.command(command)
            await Interaction.response.send_message(
                f"Operator status granted to {player},  {response}"
            )

    @world.command(
        name="place",
        description="Usage <feature> <x> <y> <z> [rotation] [mirror] [mode]",
    )
    @has_permissions(manage_channels=True)
    async def place(
        self,
        Interaction: discord.Interaction,
        feature: str,
        x: int,
        y: int,
        z: int,
        rotation: int = None,
        mirror: bool = None,
        mode: str = None,
    ):
        """Place a feature at a location. Usage <feature> <x> <y> <z> [rotation] [mirror] [mode]"""
        command = f"setblock {x} {y} {z} {feature}"
        if rotation:
            command += f" rotation={rotation}"
        if mirror:
            command += f" mirror={mirror}"
        if mode:
            command += f" mode={mode}"
        with MCRcon(rcon_host, rcon_password, port=rcon_port) as mcr:
            response = mcr.command(command)
            await Interaction.response.send_message(
                f"Placed {feature} at ({x}, {y}, {z})"
                + (f" with rotation {rotation}" if rotation else "")
                + (f", mirror {mirror}" if mirror else "")
                + (f", in mode {mode}" if mode else "")
                + "."
            )

    @world.command(name="seed", description="Get the world seed.")
    async def seed(self, Interaction: discord.Interaction):
        """Get the world seed."""
        command = "seed"
        with MCRcon(
            rcon_host, rcon_password, port=int(rcon_port)
        ) as mcr:  # Ensure port is an integer
            response = mcr.command(command)
            await Interaction.response.send_message(f"World seed: {response}")

    @world.command(
        name="setblock",
        description="Place a block at a location. Usage <x> <y> <z> <block> [mode]",
    )
    @has_permissions(manage_channels=True)
    async def setblock(
        self,
        Interaction: discord.Interaction,
        x: int,
        y: int,
        z: int,
        block: str,
        mode: str = None,
    ):
        """Place a block at a location. Usage <x> <y> <z> <block> [mode]"""
        command = f"setblock {x} {y} {z} {block}" + (f" {mode}" if mode else "")
        with MCRcon(rcon_host, rcon_password, port=rcon_port) as mcr:
            response = mcr.command(command)
            await Interaction.response.send_message(
                f"Block {block} placed at ({x}, {y}, {z})"
                + (f" in mode {mode}" if mode else "")
                + "."
            )

    @rcon.command(
        name="setidletimeout",
        description="Set the idle timeout for players. Usage <timeout>",
    )
    @has_permissions(manage_channels=True)
    async def setidletimeout(self, Interaction: discord.Interaction, timeout: int):
        """Set the idle timeout for players. Usage <timeout>"""
        command = f"setidletimeout {timeout}"
        with MCRcon(rcon_host, rcon_password, port=rcon_port) as mcr:
            response = mcr.command(command)
            await Interaction.response.send_message(
                f"Idle timeout set to {timeout} minutes."
            )

    @rcon.command(
        name="setmaxplayers",
        description="Set the maximum number of players. Usage <max_players>",
    )
    @has_permissions(manage_channels=True)
    async def setmaxplayers(self, Interaction: discord.Interaction, max_players: int):
        """Set the maximum number of players. Usage <max_players>"""
        command = f"setmaxplayers {max_players}"
        with MCRcon(rcon_host, rcon_password, port=rcon_port) as mcr:
            response = mcr.command(command)
            await Interaction.response.send_message(
                f"Maximum players set to {max_players}."
            )

    @world.command(
        name="setworldspawn", description="Set the world spawn. Usage [x y z]"
    )
    @has_permissions(manage_channels=True)
    async def setworldspawn(
        self, Interaction: discord.Interaction, x: int, y: int, z: int
    ):
        """Set the world spawn. Usage [x y z]"""
        command = f"setworldspawn {x} {y} {z}"
        with MCRcon(rcon_host, rcon_password, port=rcon_port) as mcr:
            response = mcr.command(command)
            await Interaction.response.send_message(
                f"World spawn set to ({x}, {y}, {z})."
            )

    @world.command(
        name="setspawnpoint", description="Set the world spawn. Usage [x y z]"
    )
    async def spawnpoint(
        self, Interaction: discord.Interaction, player: str, pos: str = None
    ):
        """Set the world spawn. Usage [x y z]"""
        command = f"spawnpoint {player} {pos}"
        with MCRcon(rcon_host, rcon_password, port=rcon_port) as mcr:
            response = mcr.command(command)
        await Interaction.response.send_message(
            f"Spawnpoint set to {pos} for {player}."
        )

    @rcon.command(
        name="summon", description="Summon an entity. Usage <entity> <x> <y> <z>"
    )
    @has_permissions(manage_channels=True)
    async def summon(
        self, Interaction: discord.Interaction, entity: str, x: int, y: int, z: int
    ):
        """Summon an entity. Usage <entity> <x> <y> <z>"""
        command = f"summon {entity} {x} {y} {z}"
        with MCRcon(rcon_host, rcon_password, port=rcon_port) as mcr:
            response = mcr.command(command)
            await Interaction.response.send_message(
                f"Summoned {entity} at ({x}, {y}, {z})."
            )

    @rcon.command(
        name="teleport", description="Teleport a player. Usage <player> <x> <y> <z>"
    )
    @has_permissions(manage_channels=True)
    async def teleport(
        self, Interaction: discord.Interaction, player: str, x: int, y: int, z: int
    ):
        """Teleport a player. Usage <player> <x> <y> <z>"""
        command = f"tp {player} {x} {y} {z}"
        with MCRcon(rcon_host, rcon_password, port=rcon_port) as mcr:
            response = mcr.command(command)
            await Interaction.response.send_message(
                f"Teleported {player} to ({x}, {y}, {z})."
            )

    @world.command(
        name="time", description="Set or query the world time. Usage <action> [value]"
    )
    @has_permissions(manage_channels=True)
    async def time(
        self, Interaction: discord.Interaction, action: str, value: Optional[int] = None
    ):
        """Set or query the world time. Usage <action> [value]"""
        if action.lower() == "set":
            if value is not None:
                response = await self.rcon_command(f"time set {value}")
                await Interaction.response.send_message(
                    f"Time set to {value}. Server response: {response}"
                )
            else:
                await Interaction.response.send_message(
                    "You need to provide a value for 'set' action."
                )
        elif action.lower() == "query":
            response = await self.rcon_command("time query daytime")
            await Interaction.response.send_message(f"Current time: {response}")
        else:
            await Interaction.response.send_message(
                "Invalid action. Use 'set' or 'query'."
            )


# discord setup function for the main bot to load the cog
async def setup(bot):
    """Add the cog to the bot."""
    await bot.add_cog(Quantum_RCON_Commands_Cog(bot))
