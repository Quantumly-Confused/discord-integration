
import discord
from dotenv import load_dotenv
import asyncio
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button
from json import JSONDecodeError
from io import BytesIO
import os
import aiohttp
import json
from discord import Button, ButtonStyle, InteractionType
from typing import List

#* Define the intents for the bot (this is required for the discord-py-slash-commands library)) 
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
intents.reactions = True
intents.members = True

#* Load the .env to get the discord and grafana tokens
load_dotenv()

#section Code defining the Cog and its attributes/functions

class Grafana_Discord_Integration_Cog(commands.Cog):
    def __init__(self, bot):
        """ Initializes the cog and sets up the Grafana API integration"""
        self.bot = bot
        self.logger = bot.logger
        #todo dynamic dashboard names: If possible, get a list of the dashboard names from the grafana API
        self.dashboard_names = ['minecraft-deep-dive-dashboard', 'minecraft-server-stats']
        self.panels = {}
        self.load_panel_config()
        self.panel_source = os.getenv('GRAFANA_PANEL_SOURCE')
        self.grafana_uid = os.getenv('GRAFANA_UID') 
        self.grafana_url = os.getenv('GRAFANA_URL')
        self.load_panel_config()
        
    async def panel_autocomplete(
            self,
            interaction: discord.Interaction,
            current: str) -> List[app_commands.Choice[str]]:
        print('autocomplete invoked')
        return [
            app_commands.Choice(name=panel, value=panel)
            for panel in self.panels if current.lower() in panel.lower()
        ]
    
    #discord - Integration setup command group for use with the discord-py-slash-commands library, this will group the setup related commands beneath /set.    
    grafanaset = app_commands.Group(name="grafanaset", description="Set up functions for the Grafana API Integration.")    
    @grafanaset.command(name= "panel_source", description="Set up functions for the Grafana API Integration.")
    async def set_panel_source(self, Interaction: discord.Interaction, panel_source: str):
        """
        Set the Grafana panel source.
        Usage: /set panel_source [panel_source]
        """
        os.environ['GRAFANA_PANEL_SOURCE'] = panel_source
        self.panel_source = panel_source
        await Interaction.followup.send(f"Grafana panel source set to: {panel_source}")
        
    @grafanaset.command(name = "uid", description="Set up functions for the Grafana API Integration.")
    async def set_grafana_uid(self, Interaction: discord.Interaction, grafana_uid: str):
        """
        Set the Grafana UID.
        Usage: /set uid [grafana_uid]
        """
        os.environ['GRAFANA_UID'] = grafana_uid
        self.grafana_uid = grafana_uid
        await Interaction.followup.send(f"Grafana UID set to: {grafana_uid}")
        
    @grafanaset.command(name = "url", description="Set the Grafana base url.")
    async def set_grafana_url(self, Interaction: discord.Interaction, grafana_url: str):
        """
        Set the Grafana URL.
        Usage: /set url [grafana_url]
        """
        os.environ['GRAFANA_URL'] = grafana_url
        self.grafana_url = grafana_url
        await Interaction.followup.send(f"Grafana URL set to: {grafana_url}")
    
    
        
    #todo find a way to get the content of the json modal without requiring the user to download it
    def load_panel_config(self):
        """ Loads the panel names and ids from the json modal and stores them in a dictionary
        :return: None
        """
        jsonconfig_path = 'grafana_dash_json_modal.json'
        with open(jsonconfig_path, 'r') as file:
            json_modal = json.load(file)
            self.extract_panel_config(json_modal, self.panels)
            self.logger.info(f"Panel names and ids extracted from {jsonconfig_path}")
            
            

    def extract_panel_config(self, jsonconfig, panels, parent_id=None):
        """ Recursively extracts the panel names and ids from the json modal and stores them in a dictionary
        :param jsonconfig: The json modal to extract the panel names and ids from
        :param panels: The dictionary to store the panel names and ids in
        :param parent_id: The id of the parent panel
        :return: None
        """
        if isinstance(jsonconfig, dict):
            panel_id = jsonconfig.get('id', parent_id)
            if 'title' in jsonconfig and 'id' in jsonconfig:
                panels[jsonconfig['title']] = jsonconfig['id']
            for key, value in jsonconfig.items():
                self.extract_panel_config(value, panels, panel_id)
        elif isinstance(jsonconfig, list):
            for item in jsonconfig:
                self.extract_panel_config(item, panels, parent_id)

    #section Helper functions for requesting the panel and dashboard images from the Grafana API render engine 
    async def fetch_rendered_panel(self, panel_name):
        """ Fetches the panel image from the Grafana API and sends it to the Discord channel
        :param panel_name: The name of the panel to fetch
        :return: A discord.File object containing the panel image
        """
        panel_id = self.panels.get(panel_name)
        if panel_id is not None: 
            api_key = os.getenv("GRAFANA_API_TOKEN")
            panel_source =  self.panel_source
            grafana_url = self.grafana_url
            grafana_uid = self.grafana_uid
            grafana_api_url = f"https://{grafana_url}/render/d-solo/{grafana_uid}/{panel_source}?orgId=1&panelId={panel_id}"
            headers = {'Authorization': f'Bearer {api_key}', 'Accept': 'image/png'}
            async with aiohttp.ClientSession() as session:
                self.logger.info(f'Fetching panel: {panel_name}')
                async with session.get(grafana_api_url, headers=headers) as api_response:
                    if api_response.status == 200:
                        content = await api_response.read()
                        image_stream = BytesIO(content)
                        image_stream.seek(0)

                        self.logger.info('Panel image prepared for Discord channel')
                        return discord.File(image_stream, filename="rendered_panel.png")
                    else:
                        self.logger.error(f'Failed to fetch panel: {api_response.status}')
                        
    async def fetch_rendered_multipanel(self, panel_names):
        """ Performs the same API request as fetch_rendered_panel but for multiple panels, seperated by commas in panel_names interacton
        :param panel_names: A list of panel names to fetch
        :return: A list of discord.File objects containing the panel images
        """
        panel_files = []
        for panel_name in panel_names:
            # Strip the panel names for looping the panel request
            panel_file = await self.fetch_rendered_panel(panel_name.strip())
            if panel_file:
                # Add the panel file to the list penel_files
                panel_files.append(panel_file)
        return panel_files
    
    async def dashboard_autocomplete(self, interaction: discord.Interaction, current: str):
        """ Provides autocomplete suggestions for dashboard names """
        dashboards = await self.dashboard_names()
        return [dashboard for dashboard in dashboards if current.lower() in dashboard.lower()]
    
    async def fetch_rendered_dashboard(self, dashboard_name: str, width: int, height: int):
        """ Fetches the dashboard image from the Grafana API and sends it to the Discord channel
        :param dashboard_name: The name of the dashboard to fetch
        :param width: The width of the dashboard image
        :param height: The height of the dashboard image
        :return: A discord.File object containing the dashboard image
        """
        api_key = os.getenv("GRAFANA_API_TOKEN")
        grafana_url = self.grafana_url
        grafana_uid = self.grafana_uid
        grafana_api_url = f"https://{grafana_url}/render/d/{grafana_uid}/{dashboard_name}?orgId=1&width={width}&height={height}&kiosk=tv&from=now-1h&to=now&var-machine=&var-ideal=12"     
        headers = {'Authorization': f'Bearer {api_key}', 'Accept': 'image/png'}
        # Send the request to the Grafana API and stream the content to a BytesIO object which we can pass to discord as a file. 
        async with aiohttp.ClientSession() as session:
            async with session.get(grafana_api_url, headers=headers) as api_response:
                self.logger.info(f'Fetching dashboard: {dashboard_name}')
                if api_response.status == 200:
                    content = await api_response.read()
                    image_stream = BytesIO(content)
                    image_stream.seek(0)
                    self.logger.info('Dashboard image prepared for Discord channel')
                    return discord.File(image_stream, filename="rendered_dashboard.png")
                else:
                    self.logger.error(f'Failed to fetch dashboard: {api_response.status}')
 
 
    #section Start of Discord bot commands. This command structure is based on the discord-py-slash-commands library

    #todo: add autocomplete to the dashboard and panel names
    #todo: secure the commands for server admin or moderator roles
    
    #discord - grafana command group for use with the discord-py-slash-commands library, this will group the grafana related commands beneath /grafana. 
    #discord - due to the time it takes to fetch the dashboard and panel images, all grafana api interaction responses are deferred and the user is sent a message when the image is ready to be sent.
    grafana = app_commands.Group(name="grafana", description="The Grafana discord integration cog is used to interact with the grafana API.")
    @grafana.command(name="dashboard", description="Display a Grafana dashboard")
    async def grafana_dashboard(self, Interaction: discord.Interaction, dashboard_name: str, width: int = 1800, height: int = 1200):
        """ Display a Grafana dashboard
        Usage: /grafana dashboard [dashboard_name] [width] [height]
        """
        print("Command invoked: grafana_dashboard")  # Debug print
        if Interaction.response.is_done():
            return
        await Interaction.response.defer()
        try:
            dashboard_data = await self.fetch_rendered_dashboard(dashboard_name, width, height)
            if dashboard_data:
                await Interaction.followup.send(file=dashboard_data)
                self.logger.info(f"Dashboard {dashboard_name} sent to {Interaction.user.name}")
            else:
                await Interaction.followup.send("Failed to fetch the dashboard. Please check the dashboard name and try again.")
        except Exception as e:
            await Interaction.followup.send("An error occurred while fetching the dashboard.")
            self.logger.error(f"Error fetching dashboard: {e}")
    
    # Fetches the panel image from the Grafana API and sends it to the Discord channel
    @grafana.command(name="panel", description="Display a Grafana panel")
    @app_commands.autocomplete(panel_name=panel_autocomplete)
    async def grafana_panel(self, interaction: discord.Interaction, panel_name: str): 
        """ Display a Grafana panel
        Usage: /grafana panel [panel_name]
        """
        print("Command invoked: grafana_panel")  # Debug print
        if interaction.response.is_done():
            pass
            return
        await interaction.response.defer()  # Defer the response
        print("Interaction response deferred")  # Debug print
        try:
            print(f"Fetching panel: {panel_name}")  # Debug print
            panel_data = await self.fetch_rendered_panel(panel_name)
            if panel_data:
                print(f"Panel data fetched for {panel_name}")  # Debug print
                await interaction.followup.send(file=panel_data)
                self.logger.info(f"Panel {panel_name} sent to {interaction.user.name}")
            else:
                print("Failed to fetch panel data")  # Debug print
                await interaction.followup.send("Failed to fetch the panel.")
        except Exception as e:
            self.logger.error(f"Error fetching panel: {e}")
            print(f"Exception occurred: {e}")  # Debug print
            await interaction.followup.send("An error occurred while fetching the panel.")

    # Same as the panel command, but will iterate through a list of panels seperated by commas in the panel_names interaction
    @grafana.command(name="multipanel", description="Display multiple Grafana panels")
    async def grafana_multipanel(self, interaction: discord.Interaction, panel_names: str):
        """ Display multiple Grafana panels
        Usage: /grafana multipanel [panel_names]
        """
        await interaction.response.defer()
        panel_list = [name.strip() for name in panel_names.split(',')]  # Split and strip names
        panel_files = await self.fetch_rendered_multipanel(panel_list)
        if panel_files:
            try:
                await interaction.followup.send(files=panel_files)
            except Exception as e:
                self.logger.error(f"Error sending panel files: {e}")
                await interaction.followup.send("An error occurred while sending the panels.")
        else:
            await interaction.followup.send("No panels were found or an error occurred.")
            
        
    #section: Interactive commands using Discord components
    
    @grafana.command(name="ipanel", description="Copy a Grafana panel with time range buttons")
    async def grafana_ipanel(self, interaction: discord.Interaction, panel_name: str):
        """ Render a Grafana Panel with time range buttons
        Usage: /grafana ipanel [panel_name]
        """
        await interaction.response.defer()

        view = GrafanaInteractiveView(self, panel_name)
        buttons = [
            Button(style=ButtonStyle.blue, label="1h", custom_id="1h"),
            Button(style=ButtonStyle.blue, label="6h", custom_id="6h"),
            Button(style=ButtonStyle.blue, label="12h", custom_id="12h"),
            Button(style=ButtonStyle.blue, label="24h", custom_id="24h"),
            Button(style=ButtonStyle.blue, label="7d", custom_id="7d"),
            Button(style=ButtonStyle.blue, label="30d", custom_id="30d"),
        ]
        await interaction.followup.send("Choose the panel time scope:", view=view, components=[buttons])

    @commands.Cog.listener()
    async def on_button_click(interaction):
        if interaction.component.custom_id in ["1h", "6h", "12h", "24h", "7d", "30d"]:
            await interaction.respond(
                type=InteractionType.UpdateMessage,
                content=f"You selected {interaction.component.label} time range.",
                components=[],
            )
            # TODO: Implement logic to fetch and send the panel image with the selected time range
        
        
    #! Needs work
    #todo: improve the display of the panels, maybe use a select menu
    @grafana.command(name="listpanels", description="List all panels available to display")
    async def grafana_listpanels(self, Interaction: discord.Interaction):
        """ List all panels available to display
        Usage: /grafana listpanels
        """
        panel_options = list(self.panels.keys())
        midpoint = len(panel_options) // 2
        embed = discord.Embed(title="Grafana - Available Panels", color=discord.Color.blue())
        # Splitting the panel options into two columns for the embed
        column1 = panel_options[:midpoint]
        column2 = panel_options[midpoint:]  # Fix: Define column2
        # Add the panel names to an embed
        for entry1, entry2 in zip(column1, column2):
            embed.add_field(name=entry1, value=entry2, inline=True)  # Fix: Set value to entry2
            embed.add_field(name=entry2, value='\u200b', inline=True)
            embed.add_field(name='\u200b', value='\u200b', inline=True)  # Spacer

        await Interaction.response.send_message(embed=embed)
        self.logger.info(f"Panel list sent to {Interaction.user.name}")
            

async def setup(bot):
    """ Adds the cog to the bot
    :param bot: The bot to add the cog to
    :return: None"""
    await bot.add_cog(Grafana_Discord_Integration_Cog(bot))
    
        