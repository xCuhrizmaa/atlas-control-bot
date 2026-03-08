import discord

async def agents_status(ctx):

    embed = discord.Embed(
        title="🤖 AI Agents Online",
        color=discord.Color.green()
    )

    embed.add_field(
        name="Project Manager",
        value="Coordinating builds",
        inline=False
    )

    embed.add_field(
        name="Architect Agent",
        value="Designing systems",
        inline=False
    )

    embed.add_field(
        name="Developer Agent",
        value="Writing code",
        inline=False
    )

    embed.add_field(
        name="QA Agent",
        value="Running tests",
        inline=False
    )

    embed.add_field(
        name="Security Agent",
        value="Scanning vulnerabilities",
        inline=False
    )

    await ctx.send(embed=embed)