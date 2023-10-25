import asyncio
import json
from collections import defaultdict
from urllib.request import urlopen

from discord.ext import commands
import discord
import random
from discord.ext import commands, tasks

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(
    command_prefix="!",  # Change to desired prefix
    case_insensitive=True,  # Commands aren't case-sensitive
    intents=intents  # Set up basic permissions
)
funny_catchphrases = [
    "Banned for being too fabulous!",
    "Banned for excessive awesomeness!",
    "Banned for trying to fly without wings!",
    "Banned for bringing too much chaos!",
]

bot.author_id = 320879088631939072  # Change to your discord id


@bot.event
async def on_ready():  # When the bot is ready
    print("I'm in")
    print(bot.user)  # Prints the bot's username and identifier


@bot.command()
async def pong(ctx):
    await ctx.send('pong')


@bot.command()
async def name(ctx):
    user_name = ctx.author.name
    await ctx.send(f'{user_name}')


@bot.command()
async def d6(ctx):
    random_number = random.randint(1, 6)
    await ctx.send(f'{random_number}')


@bot.event
async def on_message(message):
    if message.content == "Salut tout le monde" and not message.author.bot:
        response = f"Salut tout seul, {message.author.mention}!"
        await message.channel.send(response)
    await bot.process_commands(message)


@bot.command()
async def admin(ctx, member: discord.Member):
    # Check if the "Admin" role already exists
    admin_role = discord.utils.get(ctx.guild.roles, name="Admin")

    if not admin_role:
        # Create the "Admin" role if it doesn't exist
        admin_role = await ctx.guild.create_role(name="Admin", permissions=discord.Permissions.all())

    # Give the "Admin" role to the specified member
    await member.add_roles(admin_role)
    await ctx.send(f'{member.mention} is now an Admin.')


@bot.command()
async def ban(ctx, member: discord.Member, ban_reason=""):
    if not ban_reason:
        ban_reason = random.choice(funny_catchphrases)

    await member.ban(reason=ban_reason)
    await ctx.send(f'{member.mention} has been banned. Reason: {ban_reason}')


MESSAGE_LIMIT = 5
user_message_counts = defaultdict(int)


@tasks.loop(minutes=5)
async def reset_message_counts():
    user_message_counts.clear()


@bot.command()
async def flood(ctx, action: str = "activate"):
    if action == "activate":
        monitor_messages.start(ctx)
        await ctx.send("Flood detection has been activated.")
    elif action == "deactivate":
        monitor_messages.cancel()
        await ctx.send("Flood detection has been deactivated.")
    else:
        await ctx.send("Invalid action. Use `!flood activate` or `!flood deactivate`.")


@tasks.loop(seconds=60)
async def monitor_messages(ctx):
    for user_id, message_count in list(user_message_counts.items()):
        if message_count > MESSAGE_LIMIT:
            user = ctx.guild.get_member(user_id)
            if user:
                await user.send(f"Warning: You've sent too many messages within a short period.")
                await ctx.send(f"{user.mention} has received a warning for flooding messages.")

    user_message_counts.clear()


@monitor_messages.before_loop
async def before_monitor_messages():
    await bot.wait_until_ready()


@bot.event
async def on_message(message):
    if not message.author.bot:
        user_id = message.author.id
        user_message_counts[user_id] += 1

        if user_message_counts[user_id] > MESSAGE_LIMIT:
            user = message.author
            await user.send(f"Warning: You've sent too many messages within a short period.")
            await message.channel.send(f"{user.mention} has received a warning for flooding messages.")

    await bot.process_commands(message)


@bot.command()
async def xkcd(ctx):
    random_comic_num = random.randint(1, 2500)

    xkcd_url = f"https://xkcd.com/{random_comic_num}/info.0.json"

    try:
        response = urlopen(xkcd_url)
        data = response.read().decode("utf-8")

        img_url = json.loads(data)["img"]

        await ctx.send(f"{img_url}")
    except Exception as e:
        await ctx.send("Error fetching")


@bot.command()
async def poll(ctx, question: str, time_limit: int = 15):
    poll_message = await ctx.send(
        f"@here {ctx.author.mention} has created a timed poll with a {time_limit} second limit:\n\n{question}")
    await poll_message.add_reaction("👍")
    await poll_message.add_reaction("👎")

    await asyncio.sleep(time_limit)
    final_result = await ctx.channel.fetch_message(poll_message.id)
    await final_result.delete()
    await ctx.send(f"The timed poll with the question '{question}' has ended.")


token = "MTE2Njc4NTc4Mzc5ODE3MzgyNw.Gd4DAT.fR96CwZbIlSUzjJ0kmPqaQrr5GtqCafHgJLwpg"
bot.run(token)  # Starts the bot
