# The-Card-Game-Bot
Play Well Known Card Games in Discord!

## Prerequisites

Have the following installed on your system:

1. **[Python 3.10+](https://www.python.org/downloads/)**
2. **[Poetry (For installing required packages)](https://python-poetry.org/docs/#installation)**

## Required Packages

Using **[Poetry](https://python-poetry.org/docs/#installation)** (or manually), please install the following packages using `poetry install`: 

1. **[discord.py](https://pypi.org/project/discord.py)**

## Configuration

In order to run the bot, you will need to create an Application on the **[Discord Developer Portal](https://www.discord.com/developers)** where you will obtain a **Bot Token**

Once you have done that, you will need to copy the Bot Token and paste it into config.json in the top directory. Make sure the file contains the following:

```json
{
  "bot-token": "{INSERT BOT TOKEN HERE}",
  "debug-token": "{INSERT DEBUG BOT TOKEN HERE}",
  "debug": bool
}
```
If you do not want to use the debug features just set `"debug-token"` to the same as `"bot-token"` and `"debug"` to `false` 
