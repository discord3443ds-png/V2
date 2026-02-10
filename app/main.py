# app/main.py

import os
import threading
import time

from fastapi import FastAPI
from pydantic import BaseModel

import discord
from discord.ext import commands

# ------------ GLOBALER ZUSTAND ------------
# Hier speichern wir die letzte Announcement-Message + Timestamp
announcement_state = {
    "message": None,
    "time": 0.0
}

# ------------ FASTAPI (HTTP für Roblox) ------------

app = FastAPI()

class Announcement(BaseModel):
    message: str | None = None

@app.get("/nullix/announcement")
def get_announcement():
    # Wird von den Roblox-Skripten gepollt
    return announcement_state

@app.post("/nullix/announcement")
def set_announcement(data: Announcement):
    if data.message:
        announcement_state["message"] = data.message
        announcement_state["time"] = time.time()
    return announcement_state

# ------------ DISCORD BOT ------------

TOKEN    = os.environ.get("DISCORD_TOKEN")
GUILD_ID = int(os.environ.get("DISCORD_GUILD_ID") or "0")  # optional: nur dieser Server

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"[BOT] Eingeloggt als {bot.user}")

# Slash-Command /anc <text>
@bot.tree.command(name="anc", description="Announcement an alle Nullix-Clients senden.")
async def anc_cmd(interaction: discord.Interaction, text: str):
    """
    Usage: /anc Dein Text hier
    """
    # Setzt globale Nachricht
    set_announcement(Announcement(message=text))
    await interaction.response.send_message(f"Announcement gesendet: {text}", ephemeral=False)

@bot.event
async def setup_hook():
    # Slash-Commands synchronisieren – optional nur auf einen Server
    try:
        if GUILD_ID != 0:
            guild = discord.Object(id=GUILD_ID)
            bot.tree.copy_global_to(guild=guild)
            await bot.tree.sync(guild=guild)
            print(f"[BOT] Slash-Commands nur für Guild {GUILD_ID} synchronisiert.")
        else:
            await bot.tree.sync()
            print("[BOT] Slash-Commands global synchronisiert.")
    except Exception as e:
        print("[BOT] Fehler bei setup_hook:", e)

# ------------ BOT IM HINTERGRUND STARTEN ------------

def start_discord_bot():
    if not TOKEN:
        print("[BOT] Kein DISCORD_TOKEN in Env gesetzt!")
        return
    try:
        bot.run(TOKEN)
    except Exception as e:
        print("[BOT ERROR]", e)

# Wenn uvicorn app.main:app startet, wird diese Datei importiert
# und wir starten den Bot in einem Thread:
threading.Thread(target=start_discord_bot, daemon=True).start()
