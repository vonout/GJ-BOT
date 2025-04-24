import os
import random
import asyncio
import colorsys
from datetime import datetime

import discord
from discord.ext import commands
from discord.ui import View, Button
from dotenv import load_dotenv

# تحميل المتغيرات البيئية
load_dotenv()

# إعداد الثوابت
TOKEN = os.getenv("DISCORD_BOT_TOKEN")  # تأكد أنك وضعت هذا في .env
GUILD_ID = 1363957347298447360
COLOR_ROLE_ID = 1364526866832162846
ANNOUNCE_CH_ID = 1364541188644012033
INFO_CHANNEL_ID = 1364731786168500335
COUNTDOWN_CH_ID = 1364747941532667987
INTERVAL_SECONDS = 30
MESSAGE_ID_FILE = "message_id.txt"

# إعداد intents
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


def generate_random_color():
    h = random.random()
    s = random.uniform(0.5, 1)
    v = random.uniform(0.7, 1)
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return discord.Color.from_rgb(int(r * 255), int(g * 255), int(b * 255))


def read_message_id():
    if os.path.exists(MESSAGE_ID_FILE):
        with open(MESSAGE_ID_FILE, "r") as f:
            try:
                return int(f.read().strip())
            except ValueError:
                return None
    return None


def save_message_id(message_id):
    with open(MESSAGE_ID_FILE, "w") as f:
        f.write(str(message_id))


class ColorRoleButtons(View):
    def __init__(self, role_id):
        super().__init__(timeout=None)
        self.role_id = role_id

    @discord.ui.button(label="🎨 الحصول على الرتبة", style=discord.ButtonStyle.success)
    async def get_rgb(self, interaction: discord.Interaction, button: Button):
        role = interaction.guild.get_role(self.role_id)
        if not role:
            return await interaction.response.send_message("❌ لم يتم العثور على الرتبة.", ephemeral=True)
        if role in interaction.user.roles:
            return await interaction.response.send_message("🔔 لديك الرتبة بالفعل!", ephemeral=True)
        await interaction.user.add_roles(role)
        await interaction.response.send_message("✅ تم منحك رتبة RGB!", ephemeral=True)

    @discord.ui.button(label="❌ إزالة الرتبة", style=discord.ButtonStyle.danger)
    async def remove_rgb(self, interaction: discord.Interaction, button: Button):
        role = interaction.guild.get_role(self.role_id)
        if not role:
            return await interaction.response.send_message("❌ لم يتم العثور على الرتبة.", ephemeral=True)
        if role not in interaction.user.roles:
            return await interaction.response.send_message("🔕 لا تملك الرتبة حالياً.", ephemeral=True)
        await interaction.user.remove_roles(role)
        await interaction.response.send_message("
