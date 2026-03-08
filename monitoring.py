import requests
import discord
from discord.ext import tasks

def check_api():

```
try:
    response = requests.get("https://google.com", timeout=3)

    if response.status_code == 200:
        return "🟢 Online", True

    return "🔴 Offline", False

except:
    return "🔴 Offline", False
```

def monitor_services():

```
@tasks.loop(minutes=5)
async def monitor(bot):

    api_status, api_ok = check_api()

    if not api_ok:

        for guild in bot.guilds:
            for channel in guild.text_channels:
                if channel.name == "errors":

                    embed = discord.Embed(
                        title="🚨 SERVICE ALERT",
                        description="API appears offline",
                        color=discord.Color.red()
                    )

                    await channel.send(embed)

return monitor
```
