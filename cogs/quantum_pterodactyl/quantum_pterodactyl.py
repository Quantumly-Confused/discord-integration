
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
            "Accept": "Application/vnd.pterodactyl.v1+json"
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
    
    @power.command(name="start")
    @app_commands.checks.has_permissions(administrator=True)
    async def start_server(self, interaction: discord.Interaction):
        """Starts the game server"""
        await interaction.response.defer()
        
        success, message = await self._send_power_signal("start")
        if success:
            await interaction.followup.send("🟢 Server is starting up...")
            self.logger.info("Server is starting up")
        else:
            await interaction.followup.send(f"❌ Failed to start server: {message}")
            self.logger.error(f"Failed to start server: {message}")

    @power.command(name="stop")
    @app_commands.checks.has_permissions(administrator=True)
    async def stop_server(self, interaction: discord.Interaction):
        """Stops the game server gracefully"""
        await interaction.response.defer()
        
        success, message = await self._send_power_signal("stop")
        if success:
            await interaction.followup.send("🔴 Server is shutting down...")
            self.logger.info("Server is shutting down")
        else:
            await interaction.followup.send(f"❌ Failed to stop server: {message}")
            self.logger.error(f"Failed to stop server: {message}")

    @power.command(name="restart")
    @app_commands.checks.has_permissions(administrator=True)
    async def restart_server(self, interaction: discord.Interaction):
        """Restarts the game server"""
        await interaction.response.defer()
        
        success, message = await self._send_power_signal("restart")
        if success:
            await interaction.followup.send("🔄 Server is restarting...")
            self.logger.info("Server is restarting")
        else:
            await interaction.followup.send(f"❌ Failed to restart server: {message}")
            self.logger.error(f"Failed to restart server: {message}")

    @power.command(name="kill")
    @app_commands.checks.has_permissions(administrator=True)
    async def kill_server(self, interaction: discord.Interaction):
        """Forcefully stops the game server"""
        await interaction.response.defer()
        
        success, message = await self._send_power_signal("kill")
        if success:
            await interaction.followup.send("⚠️ Server has been forcefully stopped!")
            self.logger.warning("Server has been forcefully stopped")
        else:
            await interaction.followup.send(f"❌ Failed to kill server: {message}")
            self.logger.error(f"Failed to kill server: {message}")
            
    server = app_commands.Group(name="server", description="Server information.")
    
    @server.command(name='info', description='Get server information')
    async def server_info(self, interaction: discord.Interaction):
        await interaction.response.defer()  # Defer the response while fetching data
        url = f"{self.panel_url}/api/client"
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        server_info = data.get('attributes', {})

                        # Format and send server info
                        embed = discord.Embed(
                            title="Server Information",
                            description="Details",
                            color=discord.Color.purple()
                        )
                        embed.add_field(name="Identifier", value=server_info.get("identifier", "N/A"), inline=False)
                        embed.add_field(name="Name", value=server_info.get("name", "N/A"), inline=False)
                        embed.add_field(name="Node", value=server_info.get("node", "N/A"), inline=False)
                        embed.add_field(name="SFTP Details", value=f"Host: {server_info.get('sftp_details', {}).get('ip', 'N/A')}\nPort: {server_info.get('sftp_details', {}).get('port', 'N/A')}", inline=False)
                        embed.add_field(name="Description", value=server_info.get("description", "N/A"), inline=False)
                        embed.add_field(name="CPU Usage", value=f"{server_info.get('cpu', 'N/A')}%", inline=False)
                        embed.add_field(name="Memory Usage", value=f"{server_info.get('memory', 'N/A')} MB", inline=False)
                        
                        await interaction.followup.send(embed=embed)
                        self.logger.info("Server info fetched successfully.")
                    else:
                        error_text = await response.text()
                        await interaction.followup.send(f"Failed to fetch server info. Status: {response.status}")
                        self.logger.error(f"Failed to fetch server info: {error_text}")
        except Exception as e:
            await interaction.followup.send(f"An error occurred while fetching server info: {str(e)}")
            self.logger.error(f"Error fetching server info: {str(e)}")


async def setup(bot):
    await bot.add_cog(QuantumPterodactyl(bot))
    bot.logger.info("Cog loaded: QuantumPterodactyl v0.1")