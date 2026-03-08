import discord

async def agents_status(ctx):

```
embed = discord.Embed(
    title="AI Agents Online",
    color=discord.Color.green()
)

embed.add_field(name="Project Manager", value="Coordinating builds")
embed.add_field(name="Architect Agent", value="Designing systems")
embed.add_field(name="Developer Agent", value="Writing code")
embed.add_field(name="QA Agent", value="Testing")
embed.add_field(name="Security Agent", value="Scanning vulnerabilities")

await ctx.send(embed=embed)
```
