import discord
from discord.ext import commands, tasks
from python_aternos import Client
import datetime
import os

# 1. Setup the Discord Bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ==================== CONFIGURATION ====================
# These pull from your cloud server settings securely
ATERNOS_USER = os.getenv("ATERNOS_USER")
ATERNOS_PASS = os.getenv("ATERNOS_PASS")
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))
# =======================================================

def get_aternos_server():
    try:
        atclient = Client()
        atclient.login(ATERNOS_USER, ATERNOS_PASS)
        return atclient.account.list_servers()[0]
    except Exception as e:
        print(f"Error connecting to Aternos: {e}")
        return None

@bot.event
async def on_ready():
    print(f"🤖 Bot is online as {bot.user}")
    # Start the automated loops
    auto_start_server.start()
    auto_stop_server.start()
    auto_restart_server.start()

# =======================================================
# AUTOMATED SCHEDULES (FROM SCREENSHOT)
# =======================================================

# 🟢 Auto Start at 7:00 AM
@tasks.loop(time=datetime.time(hour=7, minute=0))
async def auto_start_server():
    channel = bot.get_channel(LOG_CHANNEL_ID)
    if channel: await channel.send("⏰ **Schedule Trigger:** Starting the server (7:00 AM)...")
    server = get_aternos_server()
    if server:
        try:
            server.start()
            if channel: await channel.send("🚀 Server is starting up automatically!")
        except Exception as e:
            if channel: await channel.send(f"⚠️ Schedule error starting server: {e}")

# 🔴 Auto Stop at 8:00 PM (20:00)
@tasks.loop(time=datetime.time(hour=20, minute=0))
async def auto_stop_server():
    channel = bot.get_channel(LOG_CHANNEL_ID)
    if channel: await channel.send("⏰ **Schedule Trigger:** Stopping the server (8:00 PM)...")
    server = get_aternos_server()
    if server:
        try:
            server.stop()
            if channel: await channel.send("🛑 Server has been shut down automatically!")
        except Exception as e:
            if channel: await channel.send(f"⚠️ Schedule error stopping server: {e}")

# ♻️ Auto Restart at 8:30 AM, 11:30 AM, 2:30 PM, and 5:30 PM
restart_times = [
    datetime.time(hour=8, minute=30),
    datetime.time(hour=11, minute=30),
    datetime.time(hour=14, minute=30),
    datetime.time(hour=17, minute=30)
]

@tasks.loop(time=restart_times)
async def auto_restart_server():
    channel = bot.get_channel(LOG_CHANNEL_ID)
    if channel: await channel.send("⏰ **Schedule Trigger:** Restarting the server...")
    server = get_aternos_server()
    if server:
        try:
            server.restart()
            if channel: await channel.send("♻️ Server is now restarting automatically!")
        except Exception as e:
            if channel: await channel.send(f"⚠️ Schedule error restarting server: {e}")


# =======================================================
# MANUAL COMMANDS
# =======================================================

@bot.command(name="start")
async def start_cmd(ctx):
    await ctx.send("⏳ Attempting manual start...")
    server = get_aternos_server()
    if not server:
        await ctx.send("❌ Failed to log into Aternos.")
        return
    try:
        server.start()
        await ctx.send("🚀 Server is starting up!")
    except Exception as e: await ctx.send(f"⚠️ Error: {e}")

@bot.command(name="stop")
async def stop_cmd(ctx):
    await ctx.send("⏳ Attempting manual stop...")
    server = get_aternos_server()
    if not server:
        await ctx.send("❌ Failed to log into Aternos.")
        return
    try:
        server.stop()
        await ctx.send("🛑 Server has been ordered to stop.")
    except Exception as e: await ctx.send(f"⚠️ Error: {e}")

@bot.command(name="restart")
async def restart_cmd(ctx):
    await ctx.send("⏳ Attempting manual restart...")
    server = get_aternos_server()
    if not server:
        await ctx.send("❌ Failed to log into Aternos.")
        return
    try:
        server.restart()
        await ctx.send("♻️ Server is restarting!")
    except Exception as e: await ctx.send(f"⚠️ Error: {e}")

# Read the bot token from variables securely
bot.run(os.getenv("DISCORD_TOKEN"))