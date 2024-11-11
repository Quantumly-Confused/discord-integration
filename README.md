# QCAdmin Discord Bot Documentation

Quantum Craft is a Discord bot built for managing and interacting with various services on the Quantumly Confused gaming Discord server. This bot is structured as a cog loader, supporting multiple cogs that integrate functionalities for Discord server management, Grafana, Pterodactyl server control, and Minecraft RCON commands. 

By default - no cogs are loaded, allowing for modular deployment and configuration per cog.

### Environment Configuration

The bot requires several environment variables. If you are not loading the specific function these variables are not required to be supplied:

- **Discord Bot Token**: `DISCORD_API_TOKEN` **REQUIRED AS A BASE**
- **Grafana**:
  - `GRAFANA_API_TOKEN`
  - `GRAFANA_PANEL_SOURCE`
  - `GRAFANA_UID`
  - `GRAFANA_URL`
- **Pterodactyl**:
  - `PTERODACTYL_API_KEY`
  - `PTERODACTYL_PANEL_URL`
  - `PTERODACTYL_SERVER_ID`
- **Minecraft**:
  - `RCON_HOST`
  - `RCON_PASSWORD`
  - `RCON_PORT`

These variables should be provided in the Docker run or other environment where python-dotenv is supported when starting main.py. 

## Table of Contents

1. [Bot Setup (`main.py`)](#bot-setup-mainpy)
2. [Cog Modules](#cog-modules)
   - [Grafana Integration (`grafana_discord_integration.py`)](#grafana-integration-grafana_discord_integrationpy)
   - [Quantum Pterodactyl Integration (`quantum_pterodactyl.py`)](#quantum-pterodactyl-integration-quantum_pterodactylpy)
   - [Status Updater (`qc_status.py`)](#status-updater-qc_statuspy)
   - [Minecraft RCON Commands (`qc_rcon_commands.py`)](#minecraft-rcon-commands-qc_rcon_commandspy)
3. [Dependencies (`requirements.txt`)](#dependencies-requirementstxt)
4. [Environment Configuration](#environment-configuration)
5. [Recommendations](#recommendations)

---

### Bot Setup (`main.py`)

- **Initialization**: The main bot class, `QCAdmin`, is built with the `discord.py` library. The bot uses `/` as the command prefix and has configured intents for message content, reactions, and member events.
- **Cog Management**: Dynamically loads cogs from the `cogs` folder, including:
  - `grafana_discord_integration`
  - `rcon_commands`
  - `qc_status`
  - `quantum_pterodactyl`
- **Command Groups**:
  - `/admin`: Manages bot commands (e.g., syncing commands with Discord).
  - `/cog`: Manages cogs, allowing admins to load, unload, and reload specific bot cogs.
- **Logging**: Configured to track all bot actions and errors, storing logs in `quantumly_confused_bot.log`.

---

### Cog Modules

#### Grafana Integration (`grafana_discord_integration.py`)

The Grafana Integration cog provides commands to interact with a Grafana instance, allowing users to display dashboard and panel images directly in Discord.

- **Commands**:
  - **`/grafana dashboard`**: Displays a Grafana dashboard.
  - **`/grafana panel`**: Displays a single Grafana panel.
  - **`/grafana multipanel`**: Displays multiple panels.
  - **`/grafanaset panel_source`, `/grafanaset uid`, `/grafanaset url`**: Set the Grafana panel source, UID, and URL dynamically.

- **Features**:
  - **Autocomplete Support**: Autocomplete functionality for panel and dashboard names.
  - **Interactive Panel Options**: Button-based time range options for dynamic data display.

#### Quantum Pterodactyl Integration (`quantum_pterodactyl.py`)

The Quantum Pterodactyl cog integrates with the Pterodactyl API to manage game server power states.

- **Commands**:
  - **`/power start`**, **`/power stop`**, **`/power restart`**, **`/power kill`**: Manage server power states.
  - **`/commands`**: Lists all available Quantum Pterodactyl commands.

- **Error Handling**: Provides feedback for each command's success or failure, logging detailed information about errors.

#### Status Updater (`qc_status.py`)

The Status Updater cog periodically changes the bot’s status message, cycling through a list of pre-set messages.

- **Rotating Status Messages**: Updates every 20 minutes.
- **Message Examples**:
  - "Trying to figure out where I put my qubits."
  - "Factoring with Shor's Algorithm."
  - "Contemplating the fragility of human existence."

#### Minecraft RCON Commands (`qc_rcon_commands.py`)

The Minecraft RCON Commands cog uses RCON (Remote Console) to interact with a Minecraft server, enabling direct in-game commands from Discord.

- **Commands**:
  - **Basic Commands**: `/rcon say`, `/rcon status`, `/rcon weather`, `/rcon ban`, `/rcon give`.
  - **World Commands**: `/world fill`, `/world setblock`, `/world seed`.
  
- **Permissions**: Many commands are restricted to users with specific Discord permissions, such as `manage_channels`.

---

### Dependencies (`requirements.txt`)

The bot relies on several libraries to support Discord interactions, web requests, and secure credential management:

```plaintext
discord==2.3.2
discord-py-interactions==5.10.0
discord-typings==0.7.0
discord.py==2.3.2
aiohttp==3.10.10
mcrcon==0.7.0
python-dotenv==1.0.0
typing_extensions==4.8.0
async-timeout==4.0.3
```