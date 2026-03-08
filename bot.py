import discord
from discord.ext import commands
import os
import psutil
from dotenv import load_dotenv

from monitoring import check_api, monitor_services
from agents import agents_status
from builder import run_build_pipeline

# -----------------------------
# LOAD ENV VARIABLES
# -----------------------------
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

BOT_VERSION = "3.3.2"

# -----------------------------
# DISCORD SETUP
# -----------------------------
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)

# -----------------------------
# READY EVENT
# -----------------------------
@bot.event
async def on_ready():

    msg = f"Atlas Control connected as {bot.user}"
    print(msg)

    monitor = monitor_services()
    monitor.start(bot)

# -----------------------------
# BUILD COMMAND
# -----------------------------
@bot.command()
async def build(ctx, project_type: str):

    await run_build_pipeline(bot, ctx, project_type)

# -----------------------------
# AGENTS STATUS
# -----------------------------
@bot.command()
async def agents(ctx):

    await agents_status(ctx)

# -----------------------------
# SERVER MONITOR
# -----------------------------
@bot.command()
async def server(ctx):

    cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory().percent
    latency = round(bot.latency * 1000)

    embed = discord.Embed(
        title="🖥 Atlas Server Monitor",
        color=discord.Color.blue()
    )

    embed.add_field(name="CPU Usage", value=f"{cpu}%")
    embed.add_field(name="Memory Usage", value=f"{memory}%")
    embed.add_field(name="Discord Latency", value=f"{latency}ms")

    await ctx.send(embed=embed)

# -----------------------------
# MONITORING COMMANDS
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
# COMMAND LIST
# -----------------------------
@bot.command(name="commands", aliases=["help"])
async def command_list(ctx):

    embed = discord.Embed(
        title="Atlas Control Commands",
        color=discord.Color.purple()
    )

    embed.add_field(
        name="Monitoring",
        value="""
!status
!server
!version
!railway
""",
        inline=False
    )

    embed.add_field(
        name="Agents",
        value="""
!agents
""",
        inline=False
    )

    embed.add_field(
        name="Project Builder",
        value="""
!build api
!build website
!build mobile-app
!build barber-booking-app
!build saas
!build ecommerce
!build ai-agent
!build chatbot
!build discord-bot
""",
        inline=False
    )

    embed.set_footer(text="Atlas Dev Lab Command Center")

    await ctx.send(embed=embed)

# -----------------------------
# ERROR HANDLER
# -----------------------------
@bot.event
async def on_command_error(ctx, error):

    if isinstance(error, commands.CommandNotFound):
        return  # prevents duplicate responses

    print(error)
    await ctx.send("⚠️ An error occurred.")

# -----------------------------
# RUN BOT
# -----------------------------
bot.run(TOKEN)
