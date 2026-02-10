# app/main.py

import os
import threading

from fastapi import FastAPI
from pydantic import BaseModel

import discord
from discord.ext import commands

# Globaler Zustand, den Roblox abfragt
global_state = {
    "fly": False
}

# ---------- FastAPI-APP (HTTP-API) ----------

app = FastAPI()

class CommandUpdate(BaseModel):
    fly: bool | None = None

@app.get("/nullix/global")
def get_global_state():
    # Roblox ruft diese URL regelmäßig auf
    return global_state

@app.post("/nullix/global")
def update_global_state(cmd: CommandUpdate):
    if cmd.fly is not None:
        global_state["fly"] = cmd.fly
    return global_state

# ---------- Discord-Bot ----------

TOKEN = os.environ.get("DISCORD_TOKEN")  # Kommt von Koyeb als Env-Variable

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"[BOT] Eingeloggt als {bot.user}")

@bot.tree.command(name="fly", description="Schaltet global Fly an/aus für alle Clients.")
async def fly_cmd(interaction: discord.Interaction, state: str):
    """
    Slash-Command: /fly on  oder  /fly off
    """
    val = state.lower() in ("on", "true", "1", "an", "ein")
    global_state["fly"] = val
    await interaction.response.send_message(f"Global Fly = {val}", ephemeral=False)

@bot.event
async def setup_hook():
    await bot.tree.sync()
    print("[BOT] Slash-Commands synchronisiert.")

# ---------- Bot beim Import starten ----------

def start_discord_bot():
    if not TOKEN:
        print("[BOT] Kein DISCORD_TOKEN gesetzt!")
        return
    try:
        bot.run(TOKEN)
    except Exception as e:
        print("[BOT ERROR]", e)

# Wenn uvicorn app.main:app lädt, wird diese Datei importiert
# und wir starten den Bot in einem Thread:
threading.Thread(target=start_discord_bot, daemon=True).start()