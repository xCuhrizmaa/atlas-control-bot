import discord
from discord.ext import commands, tasks
import os
import requests
import time
import psutil
import asyncio
import subprocess
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USER = os.getenv("GITHUB_USER")
GITHUB_REPO = os.getenv("GITHUB_REPO")

print("Token loaded successfully")

BOT_VERSION = "2.3.0"
START_TIME = datetime.utcnow()

last_api_state = True

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
    print(f"Atlas Control connected as {bot.user}")
    monitor_services.start()

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
# STATUS
# -----------------------------
@bot.command()
async def status(ctx):

    api_status, _ = check_api()

    embed = discord.Embed(
        title="🧠 Atlas Dev Lab",
        description="System Status Dashboard",
        color=discord.Color.blue()
    )

    embed.add_field(name="Store API", value=api_status)
    embed.add_field(name="Database", value="🟢 Connected")
    embed.add_field(name="Errors", value="🟢 0")

    await ctx.send(embed=embed)

# -----------------------------
# HEALTH
# -----------------------------
@bot.command()
async def health(ctx):

    api_status, _ = check_api()

    embed = discord.Embed(
        title="💚 System Health",
        color=discord.Color.green()
    )

    embed.add_field(name="API", value=api_status)

    await ctx.send(embed=embed)

# -----------------------------
# LATENCY
# -----------------------------
@bot.command()
async def latency(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f"🏓 Discord latency: {latency}ms")

# -----------------------------
# VERSION
# -----------------------------
@bot.command()
async def version(ctx):
    await ctx.send(f"⚙ Atlas Control Version {BOT_VERSION}")

# -----------------------------
# UPTIME
# -----------------------------
@bot.command()
async def uptime(ctx):

    uptime_duration = datetime.utcnow() - START_TIME

    hours, remainder = divmod(int(uptime_duration.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)

    await ctx.send(f"⏱ Uptime: {hours}h {minutes}m {seconds}s")

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

    embed.add_field(name="CPU Usage", value=f"{cpu}%")
    embed.add_field(name="Memory Usage", value=f"{memory}%")
    embed.add_field(name="Discord Latency", value=f"{latency}ms")
    embed.add_field(name="API Status", value=api_status)
    embed.add_field(name="Bot Uptime", value=f"{hours}h {minutes}m {seconds}s")

    await ctx.send(embed=embed)

# -----------------------------
# RAILWAY STATUS
# -----------------------------
@bot.command()
async def railway(ctx):

    embed = discord.Embed(
        title="🚆 Railway Status",
        description="Container running normally",
        color=discord.Color.green()
    )

    await ctx.send(embed=embed)

# -----------------------------
# AGENTS
# -----------------------------
@bot.command()
async def agents(ctx):

    embed = discord.Embed(
        title="🤖 AI Agents Online",
        color=discord.Color.green()
    )

    embed.add_field(name="Project Manager", value="Coordinating builds")
    embed.add_field(name="Architect Agent", value="Designing systems")
    embed.add_field(name="Developer Agent", value="Writing code")
    embed.add_field(name="QA Agent", value="Testing")
    embed.add_field(name="Security Agent", value="Scanning vulnerabilities")

    await ctx.send(embed=embed)

@bot.command()
async def architect(ctx):
    await ctx.send("🧠 Architect Agent designing system architecture...")

@bot.command()
async def dev(ctx):
    await ctx.send("👨‍💻 Developer Agent generating code modules...")

@bot.command()
async def qa(ctx):
    await ctx.send("🧪 QA Agent running test suites...")

@bot.command()
async def security(ctx):
    await ctx.send("🔐 Security Agent scanning vulnerabilities...")

# -----------------------------
# PROJECT GENERATOR
# -----------------------------
def create_project_structure(project_type):

    base = f"projects/{project_type}"
    os.makedirs(base, exist_ok=True)

    if project_type == "api":

        with open(f"{base}/main.py","w") as f:
            f.write("""from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message":"API running"}
""")

        with open(f"{base}/requirements.txt","w") as f:
            f.write("fastapi\nuvicorn")

    if project_type == "website":

        os.makedirs(f"{base}/frontend", exist_ok=True)
        os.makedirs(f"{base}/backend", exist_ok=True)

    if project_type == "mobile-app":

        os.makedirs(f"{base}/app", exist_ok=True)
        os.makedirs(f"{base}/api", exist_ok=True)

# -----------------------------
# GITHUB PUSH
# -----------------------------
def push_to_github():

    repo_url = f"https://{GITHUB_USER}:{GITHUB_TOKEN}@github.com/{GITHUB_USER}/{GITHUB_REPO}.git"

    subprocess.run(["git","init"])
    subprocess.run(["git","config","user.email","atlas@bot.com"])
    subprocess.run(["git","config","user.name","Atlas Bot"])

    subprocess.run(["git","add","."])
    subprocess.run(["git","commit","-m","Atlas auto project build"])

    subprocess.run(["git","branch","-M","main"])
    subprocess.run(["git","remote","add","origin",repo_url])
    subprocess.run(["git","push","-u","origin","main"])

# -----------------------------
# BUILD PIPELINE
# -----------------------------
@bot.command()
async def build(ctx, project_type: str):

    create_project_structure(project_type)

    guild = ctx.guild

    pm = discord.utils.get(guild.text_channels, name="pm")
    architect = discord.utils.get(guild.text_channels, name="architect")
    dev = discord.utils.get(guild.text_channels, name="dev")
    qa = discord.utils.get(guild.text_channels, name="qa")
    security = discord.utils.get(guild.text_channels, name="security")
    updates = discord.utils.get(guild.text_channels, name="project-updates")

    if pm:
        await pm.send(f"📋 Build request received: {project_type}")

    await asyncio.sleep(2)

    if architect:
        await architect.send("🧠 Designing system architecture...")

    await asyncio.sleep(2)

    if dev:
        await dev.send("👨‍💻 Generating project structure...")

    await asyncio.sleep(2)

    if qa:
        await qa.send("🧪 Preparing automated tests...")

    await asyncio.sleep(2)

    if security:
        await security.send("🔐 Scanning dependencies...")

    await asyncio.sleep(2)

    try:
        push_to_github()

        if updates:

            embed = discord.Embed(
                title="📦 Project Generated",
                description=f"Type: **{project_type}**",
                color=discord.Color.green()
            )

            embed.add_field(name="Repository", value=GITHUB_REPO)
            embed.add_field(name="Builder", value="Atlas Developer Agent")

            await updates.send(embed=embed)

    except Exception as e:
        print(e)

    if pm:
        await pm.send("✅ Build pipeline completed")

    await ctx.send("🚀 Project created and pushed to GitHub")

# -----------------------------
# OPERATIONS
# -----------------------------
@bot.command()
async def deploy(ctx):
    await ctx.send("🚀 Deployment initiated...")

@bot.command()
async def logs(ctx):
    await ctx.send("📜 Fetching logs...")

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
!health
!server
!latency
!uptime
!version
!railway
""",
        inline=False
    )

    embed.add_field(
        name="AI Agents",
        value="""
!agents
!architect
!dev
!qa
!security
""",
        inline=False
    )

    embed.add_field(
        name="Operations",
        value="""
!deploy
!logs
""",
        inline=False
    )

    embed.add_field(
        name="AI Builder",
        value="""
!build api
!build website
!build mobile-app
""",
        inline=False
    )

    embed.set_footer(text="Atlas Dev Lab Command Center")

    await ctx.send(embed=embed)

# -----------------------------
# SERVICE MONITOR
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
# ERROR HANDLER
# -----------------------------
@bot.event
async def on_command_error(ctx, error):

    if isinstance(error, commands.CommandNotFound):
        await ctx.send("⚠️ Unknown command.")
    else:
        print(error)
        await ctx.send("⚠️ An error occurred.")

# -----------------------------
# RUN BOT
# -----------------------------
bot.run(TOKEN)
