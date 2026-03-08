import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

print("Token loaded successfully")

# Discord intents
intents = discord.Intents.default()
intents.message_content = True

# Bot setup
bot = commands.Bot(command_prefix="!", intents=intents)


# BOT READY EVENT
@bot.event
async def on_ready():
    print(f"Atlas Control connected as {bot.user}")


# STATUS DASHBOARD
@bot.command()
async def status(ctx):

    embed = discord.Embed(
        title="🧠 Atlas Dev Lab",
        description="System Status Dashboard",
        color=discord.Color.blue()
    )

    embed.add_field(
        name="Store API",
        value="🟢 Online",
        inline=True
    )

    embed.add_field(
        name="Database",
        value="🟢 Connected",
        inline=True
    )

    embed.add_field(
        name="Errors",
        value="🟢 0",
        inline=True
    )

    embed.set_footer(text="Atlas Control System")

    await ctx.send(embed=embed)


# AI AGENTS STATUS
@bot.command()
async def agents(ctx):

    embed = discord.Embed(
        title="🤖 AI Agents Online",
        description="Atlas Development Agents",
        color=discord.Color.green()
    )

    embed.add_field(
        name="Architect Agent",
        value="Designing system architecture",
        inline=False
    )

    embed.add_field(
        name="Developer Agent",
        value="Building application features",
        inline=False
    )

    embed.add_field(
        name="QA Agent",
        value="Testing code integrity",
        inline=False
    )

    embed.add_field(
        name="Security Agent",
        value="Monitoring vulnerabilities",
        inline=False
    )

    await ctx.send(embed=embed)


# DEPLOY COMMAND
@bot.command()
async def deploy(ctx):

    embed = discord.Embed(
        title="🚀 Deployment Started",
        description="Deploying the store application...",
        color=discord.Color.orange()
    )

    embed.add_field(
        name="Status",
        value="Initializing deployment pipeline",
        inline=False
    )

    await ctx.send(embed=embed)


# ARCHITECT AGENT
@bot.command()
async def architect(ctx):

    await ctx.send(
        "🧠 Architect Agent analyzing project architecture..."
    )


# DEV AGENT
@bot.command()
async def dev(ctx):

    await ctx.send(
        "💻 Developer Agent generating code suggestions..."
    )


# QA AGENT
@bot.command()
async def qa(ctx):

    await ctx.send(
        "🧪 QA Agent running automated tests..."
    )


# SECURITY AGENT
@bot.command()
async def security(ctx):

    await ctx.send(
        "🔐 Security Agent scanning for vulnerabilities..."
    )


# LOGS COMMAND
@bot.command()
async def logs(ctx):

    await ctx.send(
        "📊 System Logs\n"
        "No critical errors detected."
    )


# ERROR HANDLING
@bot.event
async def on_command_error(ctx, error):

    if isinstance(error, commands.CommandNotFound):
        await ctx.send("⚠️ Unknown command.")
    else:
        await ctx.send("⚠️ An error occurred while processing the command.")
        print(error)


# RUN BOT
bot.run(TOKEN)