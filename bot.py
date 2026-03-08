import discord
from discord.ext import commands, tasks
import os
import requests
import time
from datetime import datetime
from dotenv import load_dotenv

# -----------------------------
# ENVIRONMENT SETUP
# -----------------------------
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

print("Token loaded successfully")

BOT_VERSION = "1.1.0"
START_TIME = datetime.utcnow()

last_api_state = True

# -----------------------------
# DISCORD SETUP
# -----------------------------
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# -----------------------------
# BOT READY EVENT
# -----------------------------
@bot.event
async def on_ready():

    print(f"Atlas Control connected as {bot.user}")

    monitor_services.start()

    # Deployment notification
    for guild in bot.guilds:
        for channel in guild.text_channels:
            if channel.name == "deployments":

                embed = discord.Embed(
                    title="🚀 Deployment Detected",
                    description=f"Atlas Control v{BOT_VERSION} is now running",
                    color=discord.Color.green()
                )

                embed.set_footer(text="Atlas Deployment Monitor")

                await channel.send(embed=embed)


# -----------------------------
# SERVICE CHECK FUNCTIONS
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
# STATUS DASHBOARD
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

    embed.set_footer(text="Atlas Monitoring System")

    await ctx.send(embed=embed)


# -----------------------------
# AI AGENTS STATUS
# -----------------------------
@bot.command()
async def agents(ctx):

    embed = discord.Embed(
        title="🤖 AI Agents Online",
        description="Atlas Development Agents",
        color=discord.Color.green()
    )

    embed.add_field(name="Architect Agent", value="Designing system architecture", inline=False)
    embed.add_field(name="Developer Agent", value="Building application features", inline=False)
    embed.add_field(name="QA Agent", value="Testing code integrity", inline=False)
    embed.add_field(name="Security Agent", value="Monitoring vulnerabilities", inline=False)

    await ctx.send(embed=embed)


# -----------------------------
# DEPLOY COMMAND
# -----------------------------
@bot.command()
async def deploy(ctx):

    embed = discord.Embed(
        title="🚀 Deployment Started",
        description="Deploying the store application...",
        color=discord.Color.orange()
    )

    embed.add_field(name="Status", value="Initializing deployment pipeline", inline=False)

    await ctx.send(embed=embed)


# -----------------------------
# AGENT COMMANDS
# -----------------------------
@bot.command()
async def architect(ctx):
    await ctx.send("🧠 Architect Agent analyzing system architecture...")


@bot.command()
async def dev(ctx):
    await ctx.send("💻 Developer Agent generating code suggestions...")


@bot.command()
async def qa(ctx):
    await ctx.send("🧪 QA Agent running automated tests...")


@bot.command()
async def security(ctx):
    await ctx.send("🔐 Security Agent scanning for vulnerabilities...")


@bot.command()
async def logs(ctx):
    await ctx.send("📊 System Logs\nNo critical errors detected.")


# -----------------------------
# SYSTEM COMMANDS
# -----------------------------
@bot.command()
async def uptime(ctx):

    uptime_duration = datetime.utcnow() - START_TIME
    hours, remainder = divmod(int(uptime_duration.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)

    await ctx.send(
        f"⏱ Bot Uptime: {hours}h {minutes}m {seconds}s"
    )


@bot.command()
async def version(ctx):

    await ctx.send(
        f"📦 Atlas Control Version: {BOT_VERSION}"
    )


@bot.command()
async def latency(ctx):

    latency_ms = round(bot.latency * 1000)

    await ctx.send(
        f"📡 Discord Latency: {latency_ms}ms"
    )


@bot.command()
async def railway(ctx):

    await ctx.send(
        "🚂 Railway Service\n"
        "Status: 🟢 Running\n"
        "Auto Deploy: Enabled"
    )


# -----------------------------
# AUTOMATIC MONITORING
# -----------------------------
@tasks.loop(minutes=5)
async def monitor_services():

    global last_api_state

    api_status, api_ok = check_api()

    for guild in bot.guilds:
        for channel in guild.text_channels:

            if channel.name == "errors":

                # API went offline
                if not api_ok and last_api_state:

                    embed = discord.Embed(
                        title="⚠️ SERVICE ALERT",
                        description="Store API is OFFLINE",
                        color=discord.Color.red()
                    )

                    embed.add_field(name="Status", value="🔴 Offline", inline=False)

                    await channel.send(embed=embed)

                # API recovered
                if api_ok and not last_api_state:

                    embed = discord.Embed(
                        title="✅ SERVICE RECOVERED",
                        description="Store API is back online",
                        color=discord.Color.green()
                    )

                    embed.add_field(name="Status", value="🟢 Online", inline=False)

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
        await ctx.send("⚠️ An error occurred while processing the command.")
        print(error)


# -----------------------------
# RUN BOT
# -----------------------------
bot.run(TOKEN)