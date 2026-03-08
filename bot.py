import discord
from discord.ext import commands, tasks
import os
from dotenv import load_dotenv
from monitoring import check_api, monitor_services
from agents import agents_status
from builder import run_build_pipeline

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

BOT_VERSION = "3.3.0"

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# -----------------------------

# READY EVENT

# -----------------------------

@bot.event
async def on_ready():
print(f"Atlas Control connected as {bot.user}")
monitor_services.start(bot)

# -----------------------------

# BUILD COMMAND

# -----------------------------

@bot.command()
async def build(ctx, project_type: str):
await run_build_pipeline(bot, ctx, project_type)

# -----------------------------

# AGENTS

# -----------------------------

@bot.command()
async def agents(ctx):
await agents_status(ctx)

# -----------------------------

# MONITORING

# -----------------------------

@bot.command()
async def status(ctx):
api_status, _ = check_api()
await ctx.send(f"API Status: {api_status}")

@bot.command()
async def version(ctx):
await ctx.send(f"Atlas Version {BOT_VERSION}")

@bot.command()
async def railway(ctx):
await ctx.send("Railway container running normally")

# -----------------------------

# HELP

# -----------------------------

@bot.command(name="commands", aliases=["help"])
async def command_list(ctx):

```
embed = discord.Embed(title="Atlas Commands")

embed.add_field(
    name="Builder",
    value="""
```

!build api
!build website
!build mobile-app
!build saas
!build ecommerce
!build ai-agent
!build chatbot
!build discord-bot
""",
inline=False
)

```
await ctx.send(embed=embed)
```

bot.run(TOKEN)
