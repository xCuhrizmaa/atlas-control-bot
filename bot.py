import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
print("Token loaded:", TOKEN)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Atlas Control connected as {bot.user}")

@bot.command()
async def status(ctx):
    await ctx.send(
        "🧠 Atlas Dev Lab Status\n"
        "Store API: Online\n"
        "Database: Connected\n"
        "Errors: 0"
    )
@bot.command()
async def agents(ctx):
    await ctx.send(
        "🤖 AI Agents Online\n"
        "Architect Agent\n"
        "Developer Agent\n"
        "QA Agent\n"
        "Security Agent"
    )

@bot.command()
async def deploy(ctx):
    await ctx.send("🚀 Deploying store...")

bot.run(TOKEN)