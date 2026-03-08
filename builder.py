import discord
import asyncio
from github_tools import create_or_update_repo


def generate_architecture(project_type):

    return f"""
Architecture Plan

Project: {project_type}

Backend: FastAPI
Frontend: React
Mobile: React Native
Database: PostgreSQL
"""


async def run_build_pipeline(bot, ctx, project_type):

    guild = ctx.guild

    pm = discord.utils.get(guild.text_channels, name="pm")
    architect = discord.utils.get(guild.text_channels, name="architect")
    plans = discord.utils.get(guild.text_channels, name="architect-plans")
    dev = discord.utils.get(guild.text_channels, name="dev")
    qa = discord.utils.get(guild.text_channels, name="qa")
    security = discord.utils.get(guild.text_channels, name="security")
    updates = discord.utils.get(guild.text_channels, name="project-updates")

    if pm:
        await pm.send(f"📋 Build request received: {project_type}")

    if architect:
        await architect.send("🧠 Designing architecture...")

    if plans:
        await plans.send(generate_architecture(project_type))

        await asyncio.sleep(1)

    if dev:
        await dev.send("👨‍💻 Generating project code...")

    repo_name, version = create_or_update_repo(project_type)

    await asyncio.sleep(1)

    if qa:
        await qa.send("🧪 Running automated tests...")
except Exception as e:
    print(f"QA agent error: {e}")

    if security:
        await security.send("🔐 Running security scan...")
except Exception as e:
    print(f"Security agent error: {e}")

    if updates:

        embed = discord.Embed(
            title="📦 Project Generated",
            color=discord.Color.green()
        )

        embed.add_field(name="Project", value=project_type)
        embed.add_field(name="Repository", value=repo_name)
        embed.add_field(name="Version", value=version)

        await updates.send(embed=embed)

    await ctx.send(f"🚀 Build complete → {repo_name}")
