import os
import random
import asyncio
import colorsys
from datetime import datetime

import discord
from discord.ext import commands
from discord.ui import View, Button

# إعداد الثوابت
TOKEN = "MTM2NDU0NDY3MjgyNzA1MjA0Mg.GWKJqr.MBfa_Gs54LgL0_1PvYGj5iJHeD-KQUfH23U88s"
GUILD_ID = 1363957347298447360
COLOR_ROLE_ID = 1364526866832162846
ANNOUNCE_CH_ID = 1364541188644012033
INFO_CHANNEL_ID = 1364731786168500335
COUNTDOWN_CH_ID = 1364747941532667987
INTERVAL_SECONDS = 30
MESSAGE_ID_FILE = "message_id.txt"

# إعداد الـ Intents
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
        with open(MESSAGE_ID_FILE, "r") as file:
            try:
                return int(file.read().strip())
            except ValueError:
                return None
    return None


def save_message_id(message_id):
    with open(MESSAGE_ID_FILE, "w") as file:
        file.write(str(message_id))


class ColorRoleButtons(View):
    def __init__(self, role_id):
        super().__init__(timeout=None)
        self.role_id = role_id

    @discord.ui.button(label="🎨 الحصول على الرتبة", style=discord.ButtonStyle.success, custom_id="get_rgb")
    async def get_rgb(self, interaction: discord.Interaction, button: Button):
        role = interaction.guild.get_role(self.role_id)
        if role in interaction.user.roles:
            await interaction.response.send_message("🔔 لديك الرتبة بالفعل!", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("✅ تم منحك رتبة RGB!", ephemeral=True)

    @discord.ui.button(label="❌ إزالة الرتبة", style=discord.ButtonStyle.danger, custom_id="remove_rgb")
    async def remove_rgb(self, interaction: discord.Interaction, button: Button):
        role = interaction.guild.get_role(self.role_id)
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message("❎ تمت إزالة رتبة RGB.", ephemeral=True)
        else:
            await interaction.response.send_message("🔕 لا تملك الرتبة حالياً.", ephemeral=True)


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    bot.loop.create_task(color_cycle())
    info_channel = bot.get_channel(INFO_CHANNEL_ID)
    if info_channel:
        embed = discord.Embed(
            title="INFO",
            description="اكتب النص الذي تريده لتحويله إلى إيمبد، وسوف يظهر هنا.",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow())
        embed.set_footer(text=bot.guilds[0].name)
        message = await info_channel.send(embed=embed)
        await message.add_reaction("✍️")

    countdown_channel = bot.get_channel(COUNTDOWN_CH_ID)
    if countdown_channel:
        ask_msg = await countdown_channel.send(
            embed=discord.Embed(title="هل تريد بدء العد؟", description="اضغط ✅ لبدء العد من 1 إلى مليون!", color=discord.Color.orange()))
        await ask_msg.add_reaction("✅")


@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    if reaction.emoji == "✍️":
        await user.send("✏️ اكتب نص الإيمبد:")
        try:
            content = await bot.wait_for("message", timeout=60, check=lambda m: m.author == user)
            await user.send("📌 أدخل عنوان الإيمبد:")
            title = await bot.wait_for("message", timeout=60, check=lambda m: m.author == user)
            await user.send("🎨 أدخل كود اللون (#FF5733):")
            color_msg = await bot.wait_for("message", timeout=60, check=lambda m: m.author == user)
            try:
                color = discord.Color(int(color_msg.content.strip()[1:], 16))
            except:
                color = discord.Color.green()

            await user.send("📢 أدخل ID الروم الذي تريد إرسال الإيمبد إليه:")
            ch_id_msg = await bot.wait_for("message", timeout=60, check=lambda m: m.author == user)
            channel = bot.get_channel(int(ch_id_msg.content))
            if not channel:
                await user.send("❌ القناة غير موجودة.")
                return

            embed = discord.Embed(title=title.content, description=content.content, color=color, timestamp=datetime.utcnow())
            embed.set_footer(text=reaction.message.guild.name)
            try:
                old_msg = await channel.fetch_message(read_message_id())
                await old_msg.delete()
            except:
                pass
            sent = await channel.send(embed=embed)
            save_message_id(sent.id)
            await user.send("✅ تم إرسال الإيمبد!")
        except asyncio.TimeoutError:
            await user.send("❌ لم يتم الرد في الوقت المحدد.")
    
    elif str(reaction.emoji) == "✅" and reaction.message.channel.id == COUNTDOWN_CH_ID:
        await reaction.message.channel.send("✅ تم بدء العد من 1 إلى مليون! 🔢")
        for i in range(1, 1000001):
            await reaction.message.channel.send(str(i))
            await asyncio.sleep(2)


async def color_cycle():
    await bot.wait_until_ready()
    guild = bot.get_guild(GUILD_ID)
    role = guild.get_role(COLOR_ROLE_ID)
    channel = bot.get_channel(ANNOUNCE_CH_ID)
    view = ColorRoleButtons(COLOR_ROLE_ID)

    while True:
        new_color = generate_random_color()
        try:
            await role.edit(color=new_color)
            embed = discord.Embed(
                description=f"⏰ سيتم تغيير لون الرتبة خلال `{INTERVAL_SECONDS}` ثانية\n\nاستخدم الأزرار للحصول أو إزالة الرتبة.",
                color=new_color)
            embed.set_footer(text=f"{guild.name} • {datetime.now().strftime('%I:%M:%S %p')}")
            embed.set_image(url=f"https://singlecolorimage.com/get/{new_color.value:06x}/50x50")

            old_msg_id = read_message_id()
            if old_msg_id:
                try:
                    old_msg = await channel.fetch_message(old_msg_id)
                    await old_msg.delete()
                except:
                    pass

            msg = await channel.send(embed=embed, view=view)
            save_message_id(msg.id)

            for i in range(INTERVAL_SECONDS, 0, -1):
                embed.description = f"⏰ سيتم تغيير لون الرتبة خلال `{i}` ثانية\n\nاستخدم الأزرار للحصول أو إزالة الرتبة."
                await msg.edit(embed=embed, view=view)
                await asyncio.sleep(1)

        except Exception as e:
            print(f"❌ خطأ أثناء تحديث اللون أو الرسالة: {e}")
            await asyncio.sleep(5)


bot.run(TOKEN)
