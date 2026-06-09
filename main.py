import discord
from discord import app_commands, ui
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# --- إعدادات البوت ---
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Active!"
def run(): app.run(host='0.0.0.0', port=8080)
Thread(target=run).start()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# --- معرفات (IDs) ---
SUPPORT_ROLE_ID = 1513675420774699168
WELCOME_CHANNEL_ID = 1513671107679358976
ADVERTISE_CHANNEL_ID = 1513731982893256875

# --- زر الـ VIP ---
class JoinButton(ui.View):
    def __init__(self, url):
        super().__init__(timeout=None)
        self.add_item(ui.Button(label="اضغط هنا للدخول", url=url, style=discord.ButtonStyle.link))

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Logged in as {bot.user}')

# --- نظام الحماية (حذف الروابط) ---
@bot.event
async def on_message(message):
    if message.author.bot: return
    
    # السماح لروابط ديسكورد
    if "discord.gg/" in message.content or "discord.com/invite/" in message.content:
        return 

    # حذف أي رابط آخر لغير المسؤولين
    if "http" in message.content:
        role = discord.utils.get(message.guild.roles, id=SUPPORT_ROLE_ID)
        if role not in message.author.roles:
            await message.delete()

# --- الترحيب ---
@bot.event
async def on_member_join(member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        await channel.send(f"أهلاً بك {member.mention} في سيرفرنا! 🎉")

# --- أمر VIP الفخم ---
@bot.tree.command(name="vip", description="نشر سيرفر VIP بشكل احترافي")
@app_commands.checks.has_role(SUPPORT_ROLE_ID)
@app_commands.checks.cooldown(1, 300, key=lambda i: i.user.id)
async def vip(interaction: discord.Interaction, link: str, idea: str):
    channel = bot.get_channel(ADVERTISE_CHANNEL_ID)
    
    embed = discord.Embed(
        title="👑 VIP SERVER PROMOTION 👑",
        description=f"**الـفـكـرة:**\n{idea}",
        color=0xFFD700
    )
    if interaction.guild.icon:
        embed.set_thumbnail(url=interaction.guild.icon.url)
    
    embed.set_footer(text="Tickit System | Premium Advertising", icon_url=bot.user.avatar.url)
    
    await channel.send(f"|| @everyone || || @here ||")
    await channel.send(embed=embed, view=JoinButton(url=link))
    await interaction.response.send_message("✅ تم إرسال الإعلان بنجاح!", ephemeral=True)

# --- أمر Help ---
@bot.tree.command(name="help", description="معلومات عن البوت")
async def help_cmd(interaction: discord.Interaction, language: str = "ar"):
    if language.lower() == "ar":
        text = "البوت مسؤول عن نشر السيرفرات بشكل مميز. يمكنك دفع كريدت لترقية سيرفرك لـ VIP. افتح تذكرة (Ticket) للتفاصيل."
    else:
        text = "This bot handles server promotions. You can pay credits to get VIP status. Open a ticket for more details."
    await interaction.response.send_message(text, ephemeral=True)

bot.run(os.environ['DISCORD_TOKEN'])
