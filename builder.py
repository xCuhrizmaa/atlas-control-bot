import discord
import asyncio
from github_tools import create_or_update_repo


def generate_architecture(project_type):
    architecture = (
        "Architecture Plan\n\n"
        f"Project: {project_type}\n\n"
        "Backend: FastAPI\n"
        "Frontend: React\n"
        "Mobile: React Native\n"
        "Database: PostgreSQL\n"
    )
    return architecture


async def run_build_pipeline(bot, ctx, project_type):

    guild = ctx.guild

    pm = discord.utils.get(guild.text_channels, name="pm")
    architect = discord.utils.get(guild.text_channels, name="architect")
    plans = discord.utils.get(guild.text_channels, name="architect-plans")
    dev = discord.utils.get(guild.text_channels, name="dev")
    qa = discord.utils.get(guild.text_channels, name="qa")
    security = discord.utils.get(guild.text_channels, name="security")
    updates = discord.utils.get(guild.text_channels, name="project-updates")

    # PM
    if pm:
        await pm.send(f"📋 Build request received: {project_type}")

    # Architect
    if architect:
        await architect.send("🧠 Designing architecture...")

    # Architecture plan
    if plans:
        await plans.send(generate_architecture(project_type))

    await asyncio.sleep(1)

    # Developer
    if dev:
        await dev.send("👨‍💻 Generating project code...")

    repo_name, version = create_or_update_repo(project_type)

    await asyncio.sleep(1)

    # QA
    if qa:
        await qa.send("🧪 Running automated tests...")

    # Security
    if security:
        await security.send("🔐 Running security scan...")

    # Project updates
    if updates:
        embed = discord.Embed(
            title="📦 Project Generated",
            color=discord.Color.green()
        )

        embed.add_field(name="Project", value=project_type, inline=False)
        embed.add_field(name="Repository", value=repo_name, inline=False)
        embed.add_field(name="Version", value=version, inline=False)

        await updates.send(embed=embed)

    await ctx.send(f"🚀 Build complete → {repo_name}")
