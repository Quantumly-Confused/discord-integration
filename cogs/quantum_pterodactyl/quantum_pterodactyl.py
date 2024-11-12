
# QuantumPterodactyl: A cog which uses Discord Interactions to send commands to the Pterodactyl server API. 
# 
#Author:
#    Dave Chadwick (github.com/ropeadope62)
# Version:
#    0.1


import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
import os
from dotenv import load_dotenv
import logging

class QuantumPterodactyl(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # We will use the same logger as we use for the client in QCAdmin loaded cogs
        self.logger = bot.logger
        load_dotenv()
        self.api_key = os.getenv('PTERODACTYL_API_KEY')
        self.panel_url = os.getenv('PTERODACTYL_PANEL_URL')  
        self.server_id = os.getenv('PTERODACTYL_SERVER_ID')
        
        if not all([self.api_key, self.panel_url, self.server_id]):
            self.logger.error("Missing required Pterodactyl dotenv variables")
            raise ValueError("Missing required Pterodactyl dotenv variables")
        
    @app_commands.command(name="commands", description="List all QuantumPterodactyl commands")
    async def list_commands(self, interaction: discord.Interaction):
        """QuantumPterodactyl command list:"""
        commands_list = [
            "/power state <serverid:str> - Get the current state of the game server",
            "/power start <serverid:str> - Starts the game server",
            "/power stop <serverid:str> - Stops the game server gracefully",
            "/power restart <serverid:str> - Restarts the game server",
            "/power kill <serverid:str> - Forcefully stops the game server",
            "/commands - Lists all available QuantumPterodactyl commands"
        ]
        commands_message = "\n".join(commands_list)
        await interaction.response.send_message(f"**QuantumPterodactyl Commands:**\n{commands_message}")
        embed = discord.Embed(title="QuantumPterodactyl Commands", description="List of all available commands", color=discord.Color.blue())
        for command in commands_list:
            name, description = command.split(" - ")
            embed.add_field(name=name, value=description, inline=False)
        
        await interaction.response.send_message(embed=embed)
        
    async def _send_power_signal(self, signal: str, server_id: str) -> tuple[bool, str]:
        """
        Send a power signal to the Quantumly Confused Pterodactyl server.
        
        Args:
            signal (str): One of 'start', 'stop', 'restart', 'kill'
            server_id (str): The server ID to target for the power signal
        """
        url = f"{self.panel_url}/api/client/servers/{server_id}/power"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        data = {"signal": signal}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=data) as response:
                    if response.status == 204:  # Success with no content
                        self.logger.info(f"Successfully sent {signal} signal to server {server_id}")
                        return True, f"Successfully sent {signal} signal to server {server_id}"
                    else:
                        error_text = await response.text()
                        self.logger.error(f"Pterodactyl API error: {error_text}")
                        return False, f"Failed to send {signal} signal. Status: {response.status}"
        except Exception as e:
            self.logger.error(f"Error sending power signal to server {server_id}: {str(e)}")
            return False, f"Error occurred: {str(e)}"


    power = app_commands.Group(name="power", description="Control server power state.")
    
    @power.command(name="start")
    @app_commands.checks.has_permissions(administrator=True)
    async def start_server(self, interaction: discord.Interaction, server_id: str):
        """Starts the specified game server"""
        await interaction.response.defer() #Discord: always defer the response when using interactions that may take longer than 3 seconds to respond
        
        success, message = await self._send_power_signal("start", server_id)
        
        if success:
            await interaction.followup.send(f"🟢 Server `{server_id}` is starting up...")
            self.logger.info(f"Server `{server_id}` is starting up")
        else:
            await interaction.followup.send(f"❌ Failed to start server `{server_id}`: {message}")
            self.logger.error(f"Failed to start server `{server_id}`: {message}")


    @power.command(name="stop")
    @app_commands.checks.has_permissions(administrator=True)
    async def stop_server(self, interaction: discord.Interaction, server_id: str):
        """Stops the specified game server gracefully"""
        await interaction.response.defer()

        success, message = await self._send_power_signal("stop", server_id)
        
        if success:
            await interaction.followup.send(f"🔴 Server `{server_id}` is shutting down...")
            self.logger.info(f"Server `{server_id}` is shutting down")
        else:
            await interaction.followup.send(f"❌ Failed to stop server `{server_id}`: {message}")
            self.logger.error(f"Failed to stop server `{server_id}`: {message}")


    @power.command(name="restart")
    @app_commands.checks.has_permissions(administrator=True)
    async def restart_server(self, interaction: discord.Interaction, server_id: str):
        """Restarts the specified game server"""
        await interaction.response.defer()

        success, message = await self._send_power_signal("restart", server_id)
        
        if success:
            await interaction.followup.send(f"🔄 Server `{server_id}` is restarting...")
            self.logger.info(f"Server `{server_id}` is restarting")
        else:
            await interaction.followup.send(f"❌ Failed to restart server `{server_id}`: {message}")
            self.logger.error(f"Failed to restart server `{server_id}`: {message}")


    @power.command(name="kill")
    @app_commands.checks.has_permissions(administrator=True)
    async def kill_server(self, interaction: discord.Interaction, server_id: str):
        """Forcefully stops the specified game server"""
        await interaction.response.defer()

        success, message = await self._send_power_signal("kill", server_id)
        
        if success:
            await interaction.followup.send(f"⚠️ Server `{server_id}` has been forcefully stopped!")
            self.logger.warning(f"Server `{server_id}` has been forcefully stopped")
        else:
            await interaction.followup.send(f"❌ Failed to kill server `{server_id}`: {message}")
            self.logger.error(f"Failed to kill server `{server_id}`: {message}")
    
    @power.command(name="state")
    @app_commands.checks.has_permissions(administrator=True)
    async def power_state(self, interaction: discord.Interaction, server_id: str):
        """Fetches and displays the current power state of the specified server"""
        await interaction.response.defer()

        url = f"{self.panel_url}/api/client/servers/{server_id}/resources"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        power_state = data.get('attributes', {}).get('current_state', 'Unknown')

                        # Send the power state as a message
                        await interaction.followup.send(f"The current power state of server `{server_id}` is: `{power_state}`")
                        self.logger.info(f"Power state fetched for server `{server_id}`: {power_state}")
                    else:
                        error_text = await response.text()
                        self.logger.error(f"Pterodactyl API error: {error_text}")
                        await interaction.followup.send(f"❌ Failed to fetch power state. Status: {response.status}")
        except Exception as e:
            self.logger.error(f"Error fetching power state for server `{server_id}`: {str(e)}")
            await interaction.followup.send(f"❌ Error occurred: {str(e)}")
            
    server = app_commands.Group(name="server", description="Server information.")
    
    @server.command(name="list", description="List all game servers")
    @app_commands.checks.has_permissions(administrator=True, manage_guild=True)
    async def list_servers(self, interaction: discord.Interaction):
        """
        Lists all servers associated with the Pterodactyl panel.
        """
        await interaction.response.defer()

        url = f"{self.panel_url}/api/client/servers"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        server_list = [f"{server['attributes']['name']} (ID: {server['attributes']['id']})" for server in data['data']]
                        formatted_list = "\n".join(server_list)
                        await interaction.followup.send(f"**Servers:**\n{formatted_list}")
                    else:
                        error_text = await response.text()
                        self.logger.error(f"Pterodactyl API error: {error_text}")
                        await interaction.followup.send(f"❌ Failed to list servers. Status: {response.status}")
        except Exception as e:
            self.logger.error(f"Error listing servers: {str(e)}")
            await interaction.followup.send(f"❌ Error occurred: {str(e)}")
        
    
    
# QuantumPterodactyl: A cog which uses Discord Interactions to send commands to the Pterodactyl server API. 
# 
#Author:
#    Dave Chadwick (github.com/ropeadope62)
# Version:
#    0.1


import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
import os
from dotenv import load_dotenv
import logging

class QuantumPterodactyl(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # We will use the same logger as we use for the client in QCAdmin loaded cogs
        self.logger = bot.logger
        load_dotenv()
        self.api_key = os.getenv('PTERODACTYL_API_KEY')
        self.panel_url = os.getenv('PTERODACTYL_PANEL_URL')  
        self.server_id = os.getenv('PTERODACTYL_SERVER_ID')
        
        if not all([self.api_key, self.panel_url, self.server_id]):
            self.logger.error("Missing required Pterodactyl dotenv variables")
            raise ValueError("Missing required Pterodactyl dotenv variables")
        
    @app_commands.command(name="commands", description="List all QuantumPterodactyl commands")
    async def list_commands(self, interaction: discord.Interaction):
        """QuantumPterodactyl command list:"""
        commands_list = [
            
            "/power start - Starts the game server",
            "/power stop - Stops the game server gracefully",
            "/power restart - Restarts the game server",
            "/power kill - Forcefully stops the game server",
            "/server list - Lists all game servers",
            "/server info - Get server information",
            "/commands - Lists all available QuantumPterodactyl commands"
        ]
        commands_message = "\n".join(commands_list)
        await interaction.response.send_message(f"**QuantumPterodactyl Commands:**\n{commands_message}")
        embed = discord.Embed(title="QuantumPterodactyl Commands", description="List of all available commands", color=discord.Color.blue())
        for command in commands_list:
            name, description = command.split(" - ")
            embed.add_field(name=name, value=description, inline=False)
        
        await interaction.response.send_message(embed=embed)
        
    async def _send_power_signal(self, signal: str) -> tuple[bool, str]:
        """
        Send a power signal to the Quantumly Confused Pterodactyl server.
        
        Args:
            signal (str): One of 'start', 'stop', 'restart', 'kill'
        """
        url = f"{self.panel_url}/api/client/servers/{self.server_id}/power"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        data = {"signal": signal}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=data) as response:
                    if response.status == 204:  # Success with no content
                        self.logger.info(f"Successfully sent {signal} signal to server")
                        return True, f"Successfully sent {signal} signal to server"
                    else:
                        error_text = await response.text()
                        self.logger.error(f"Pterodactyl API error: {error_text}")
                        return False, f"Failed to send {signal} signal. Status: {response.status}"
        except Exception as e:
            self.logger.error(f"Error sending power signal: {str(e)}")
            return False, f"Error occurred: {str(e)}"

    power = app_commands.Group(name="power", description="Control server power state.")
    
    @power.command(name="stop")
    @app_commands.checks.has_permissions(administrator=True)
    async def stop_server(self, interaction: discord.Interaction, server_id: str):
        """Stops the specified game server gracefully"""
        await interaction.response.defer() #Discord: with interactions its common to defer the response so that the interaction doesn't time out (3s) while the command is being processed

        success, message = await self._send_power_signal("stop", server_id)
        
        if success:
            await interaction.followup.send(f"🔴 Server `{server_id}` is shutting down...")
            self.logger.info(f"Server `{server_id}` is shutting down")
        else:
            await interaction.followup.send(f"❌ Failed to stop server `{server_id}`: {message}")
            self.logger.error(f"Failed to stop server `{server_id}`: {message}")

    @power.command(name="restart")
    @app_commands.checks.has_permissions(administrator=True)
    async def restart_server(self, interaction: discord.Interaction, server_id: str):
        """Restarts the specified game server"""
        await interaction.response.defer() #Discord: Defer all interactions which may take longer than 3 seconds to respond

        success, message = await self._send_power_signal("restart", server_id)
        
        if success:
            await interaction.followup.send(f"🔄 Server `{server_id}` is restarting...")
            self.logger.info(f"Server `{server_id}` is restarting")
        else:
            await interaction.followup.send(f"❌ Failed to restart server `{server_id}`: {message}")
            self.logger.error(f"Failed to restart server `{server_id}`: {message}")

    @power.command(name="kill")
    @app_commands.checks.has_permissions(administrator=True)
    async def kill_server(self, interaction: discord.Interaction, server_id: str):
        """Forcefully stops the specified game server"""
        await interaction.response.defer() 

        success, message = await self._send_power_signal("kill", server_id)
        
        if success:
            await interaction.followup.send(f"⚠️ Server `{server_id}` has been forcefully stopped!")
            self.logger.warning(f"Server `{server_id}` has been forcefully stopped")
        else:
            await interaction.followup.send(f"❌ Failed to kill server `{server_id}`: {message}")
            self.logger.error(f"Failed to kill server `{server_id}`: {message}")
            
    server = app_commands.Group(name="server", description="Server information.") #Discord: Define the app command group for 'server' commands
    
    @server.command(name="list", description="List all game servers")
    @app_commands.checks.has_permissions(administrator=True, manage_guild=True)
    async def list_servers(self, interaction: discord.Interaction):
        """
        Lists all servers associated with the Pterodactyl panel.
        """
        await interaction.response.defer() 

        url = f"{self.panel_url}/api/client/servers"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        server_list = [f"**{server['attributes']['name']}** (ID: {server['attributes']['id']})" for server in data['data']]

                        embed = discord.Embed(
                            title="Pterodactyl Servers",
                            description="\n".join(server_list),
                            color=discord.Color.purple()
                        )
                        await interaction.followup.send(embed=embed)
                    else:
                        error_text = await response.text()
                        self.logger.error(f"Pterodactyl API error: {error_text}")
                        await interaction.followup.send(f"❌ Failed to list servers. Status: {response.status}")
        except Exception as e:
            self.logger.error(f"Error listing servers: {str(e)}")
            await interaction.followup.send(f"❌ Error occurred: {str(e)}")
        
        
    @server.command(name="details", description="Get detailed information about a specific server")
    @app_commands.checks.has_permissions(administrator=True, manage_guild=True)
    async def server_details(self, interaction: discord.Interaction, server_id: str = None):
        """Fetches and displays detailed server information."""
        await interaction.response.defer()

        # Use provided server_id or default to self.server_id
        server_id = server_id or self.server_id
        url = f"{self.panel_url}/api/application/servers/{server_id}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        attributes = data['attributes']

                        # Extract core data, we can add more fields if needed this is not an exhaustive list of attributes
                        server_name = attributes.get("name", "N/A")
                        description = attributes.get("description", "No description provided")
                        uuid = attributes.get("uuid", "N/A")
                        identifier = attributes.get("identifier", "N/A")
                        suspended = "Yes" if attributes.get("suspended") else "No"

                        # Limits
                        limits = attributes.get("limits", {})
                        memory = limits.get("memory", "N/A")
                        swap = limits.get("swap", "N/A")
                        disk = limits.get("disk", "N/A")
                        io = limits.get("io", "N/A")
                        cpu = limits.get("cpu", "N/A")

                        # Feature Limits
                        feature_limits = attributes.get("feature_limits", {})
                        databases = feature_limits.get("databases", "N/A")
                        allocations = feature_limits.get("allocations", "N/A")
                        backups = feature_limits.get("backups", "N/A")

                        # Container Information
                        container = attributes.get("container", {})
                        startup_command = container.get("startup_command", "N/A")
                        image = container.get("image", "N/A")
                        installed = "Yes" if container.get("installed") else "No"

                        # Embed creation
                        embed = discord.Embed(
                            title=f"Server Details: {server_name}",
                            description=description,
                            color=discord.Color.purple()
                        )
                        embed.add_field(name="UUID", value=uuid, inline=False)
                        embed.add_field(name="Identifier", value=identifier, inline=True)
                        embed.add_field(name="Suspended", value=suspended, inline=True)

                        # Limits
                        embed.add_field(name="Memory Limit", value=f"{memory} MB", inline=True)
                        embed.add_field(name="Swap Limit", value=f"{swap} MB", inline=True)
                        embed.add_field(name="Disk Limit", value=f"{disk} MB", inline=True)
                        embed.add_field(name="I/O Limit", value=io, inline=True)
                        embed.add_field(name="CPU Limit", value=cpu, inline=True)

                        # Feature Limits
                        embed.add_field(name="Databases", value=databases, inline=True)
                        embed.add_field(name="Allocations", value=allocations, inline=True)
                        embed.add_field(name="Backups", value=backups, inline=True)

                        # Container Info
                        embed.add_field(name="Startup Command", value=startup_command, inline=False)
                        embed.add_field(name="Image", value=image, inline=True)
                        embed.add_field(name="Installed", value=installed, inline=True)

                        # Additional Information
                        embed.set_footer(text=f"Created at: {attributes.get('created_at', 'N/A')}\nUpdated at: {attributes.get('updated_at', 'N/A')}")

                        await interaction.followup.send(embed=embed)
                        self.logger.info(f"Server details fetched successfully for server ID: {server_id}")
                    else:
                        error_text = await response.text()
                        self.logger.error(f"Pterodactyl API error: {error_text}")
                        await interaction.followup.send(f"❌ Failed to fetch server details. Status: {response.status}")
        except Exception as e:
            self.logger.error(f"Error fetching server details: {str(e)}")
            await interaction.followup.send(f"❌ Error occurred: {str(e)}")

