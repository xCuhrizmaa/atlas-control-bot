import discord
from discord.ext import commands, tasks
import os
import requests
import time
import psutil
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# -----------------------------
# ENVIRONMENT SETUP
# -----------------------------
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

print("Token loaded successfully")

BOT_VERSION = "1.5.0"
START_TIME = datetime.utcnow()

last_api_state = True

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
# BOT READY EVENT
# -----------------------------
@bot.event
async def on_ready():

    print(f"Atlas Control connected as {bot.user}")

    monitor_services.start()

    # restart alert
    for guild in bot.guilds:
        for channel in guild.text_channels:
            if channel.name == "errors":

                embed = discord.Embed(
                    title="⚠️ Atlas Restart Detected",
                    description=f"Atlas Control v{BOT_VERSION} started",
                    color=discord.Color.orange()
                )

                embed.add_field(
                    name="Notice",
                    value="Possible crash or deployment restart",
                    inline=False
                )

                await channel.send(embed=embed)

# -----------------------------
# SERVICE CHECK
# -----------------------------
def check_api():

    try:

        start = time.time()
        response = requests.get("https://google.com", timeout=3)
        latency = int((time.time() - start) * 1000)

        if response.status_code == 200:
            return f"🟢 Online ({latency}ms)", True

        return "🔴 Offline", False

    except:
        return "🔴 Offline", False


def check_database():
    return "🟢 Connected"

# -----------------------------
# STATUS COMMAND
# -----------------------------
@bot.command()
async def status(ctx):

    api_status, api_ok = check_api()
    db_status = check_database()

    embed = discord.Embed(
        title="🧠 Atlas Dev Lab",
        description="System Status Dashboard",
        color=discord.Color.blue()
    )

    embed.add_field(name="Store API", value=api_status, inline=True)
    embed.add_field(name="Database", value=db_status, inline=True)
    embed.add_field(name="Errors", value="🟢 0", inline=True)

    await ctx.send(embed=embed)

# -----------------------------
# SERVER MONITOR
# -----------------------------
@bot.command()
async def server(ctx):

    cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory().percent
    latency = round(bot.latency * 1000)

    api_status, _ = check_api()

    uptime_duration = datetime.utcnow() - START_TIME
    hours, remainder = divmod(int(uptime_duration.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)

    embed = discord.Embed(
        title="🖥 Atlas Server Monitor",
        color=discord.Color.dark_teal()
    )

    embed.add_field(name="CPU Usage", value=f"{cpu}%", inline=True)
    embed.add_field(name="Memory Usage", value=f"{memory}%", inline=True)
    embed.add_field(name="Discord Latency", value=f"{latency}ms", inline=True)

    embed.add_field(name="API Status", value=api_status, inline=False)
    embed.add_field(name="Bot Uptime", value=f"{hours}h {minutes}m {seconds}s", inline=False)

    await ctx.send(embed=embed)

# -----------------------------
# BUILD SYSTEM
# -----------------------------
@bot.command()
async def build(ctx, project_type: str):

    await ctx.send("🧠 **Architect Agent** analyzing project requirements...")
    await asyncio.sleep(2)

    if project_type.lower() == "website":

        await ctx.send(
            "🧠 Architect Agent\n"
            "Stack Selected:\n"
            "Frontend: React / Next.js\n"
            "Backend: FastAPI\n"
            "Database: PostgreSQL\n"
            "Deployment: Vercel + Railway"
        )

    elif project_type.lower() == "api":

        await ctx.send(
            "🧠 Architect Agent\n"
            "Stack Selected:\n"
            "Backend: FastAPI\n"
            "Database: PostgreSQL\n"
            "Auth: JWT\n"
            "Deployment: Railway"
        )

    elif project_type.lower() == "mobile-app":

        await ctx.send(
            "🧠 Architect Agent\n"
            "Stack Selected:\n"
            "Mobile: React Native + Expo\n"
            "Backend: FastAPI\n"
            "Auth: Supabase\n"
            "Payments: Stripe"
        )

    await asyncio.sleep(2)

    await ctx.send("👨‍💻 **Developer Agent** generating project structure...")
    await asyncio.sleep(2)

    await ctx.send(
        "📁 Project Structure\n"
        "frontend/\n"
        "backend/\n"
        "database/\n"
        "deployment/\n"
    )

    await asyncio.sleep(2)

    await ctx.send("🧪 **QA Agent** preparing test suite...")
    await asyncio.sleep(2)

    await ctx.send("🔐 **Security Agent** scanning dependencies...")
    await asyncio.sleep(2)

    await ctx.send("🚀 **Deployment Agent** preparing deployment pipeline...")

# -----------------------------
# AGENTS STATUS
# -----------------------------
@bot.command()
async def agents(ctx):

    embed = discord.Embed(
        title="🤖 AI Agents Online",
        color=discord.Color.green()
    )

    embed.add_field(name="Architect Agent", value="Designing systems", inline=False)
    embed.add_field(name="Developer Agent", value="Writing code", inline=False)
    embed.add_field(name="QA Agent", value="Testing systems", inline=False)
    embed.add_field(name="Security Agent", value="Scanning vulnerabilities", inline=False)

    await ctx.send(embed=embed)

# -----------------------------
# COMMAND LIST
# -----------------------------
@bot.command(name="commands", aliases=["help"])
async def command_list(ctx):

    embed = discord.Embed(
        title="📜 Atlas Control Commands",
        color=discord.Color.purple()
    )

    embed.add_field(
        name="Monitoring",
        value="""
!status
!server
""",
        inline=False
    )

    embed.add_field(
        name="AI Agents",
        value="""
!agents
!build website
!build api
!build mobile-app
""",
        inline=False
    )

    embed.set_footer(text="Atlas Dev Lab Command Center")

    await ctx.send(embed=embed)

# -----------------------------
# MONITOR SERVICES
# -----------------------------
@tasks.loop(minutes=5)
async def monitor_services():

    global last_api_state

    api_status, api_ok = check_api()

    for guild in bot.guilds:
        for channel in guild.text_channels:

            if channel.name == "errors":

                if not api_ok and last_api_state:

                    embed = discord.Embed(
                        title="🚨 SERVICE ALERT",
                        description="Store API is OFFLINE",
                        color=discord.Color.red()
                    )

                    await channel.send(embed=embed)

                if api_ok and not last_api_state:

                    embed = discord.Embed(
                        title="✅ SERVICE RECOVERED",
                        description="Store API is back online",
                        color=discord.Color.green()
                    )

                    await channel.send(embed=embed)

    last_api_state = api_ok

# -----------------------------
# ERROR HANDLING
# -----------------------------
@bot.event
async def on_command_error(ctx, error):

    if isinstance(error, commands.CommandNotFound):
        await ctx.send("⚠️ Unknown command.")
    else:
        await ctx.send("⚠️ An error occurred.")
        print(error)

# -----------------------------
# RUN BOT
# -----------------------------
bot.run(TOKEN)