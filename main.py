import discord
from discord import app_commands
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# إعداد Flask لإبقاء البوت نشطاً على Render
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is running!"
def run(): app.run(host='0.0.0.0', port=8080)
Thread(target=run).start()

# إعداد البوت
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

SUPPORT_ROLE_ID = 1513675420774699168
WELCOME_CHANNEL_ID = 1513671107679358976
ADVERTISE_CHANNEL_ID = 1513731982893256875

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Logged in as {bot.user}')

# حذف الروابط
@bot.event
async def on_message(message):
    if message.author.bot: return
    
    # التحقق إذا كان الرابط ديسكورد
    if "discord.gg/" in message.content or "discord.com/invite/" in message.content:
        return # مسموح

    # حذف أي رابط آخر إذا لم يكن الشخص من الرتبة المسموحة
    if "http" in message.content:
        role = discord.utils.get(message.guild.roles, id=SUPPORT_ROLE_ID)
        if role not in message.author.roles:
            await message.delete()

    await bot.process_commands(message)

# الترحيب
@bot.event
async def on_member_join(member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        await channel.send(f"أهلاً بك {member.mention} في سيرفرنا!")

# أمر /server
@bot.tree.command(name="server", description="نشر السيرفر")
@app_commands.checks.has_role(SUPPORT_ROLE_ID)
async def server(interaction: discord.Interaction, link: str, idea: str):
    channel = bot.get_channel(ADVERTISE_CHANNEL_ID)
    embed = discord.Embed(title="🚀 إعلان سيرفر جديد", description=f"**الرابط:** {link}\n**الفكرة:** {idea}", color=0xFFD700)
    await channel.send(f"|| @everyone || || @here ||", embed=embed)
    await interaction.response.send_message("تم نشر السيرفر بنجاح!", ephemeral=True)

# أمر /help
@bot.tree.command(name="help", description="معلومات عن البوت")
async def help_cmd(interaction: discord.Interaction, language: str = "ar"):
    if language.lower() == "ar":
        text = "هذا البوت متخصص في نشر السيرفرات... (أضف التفاصيل هنا)"
    else:
        text = "This bot is specialized in server advertising... (Add details here)"
    await interaction.response.send_message(text)

bot.run(os.environ['DISCORD_TOKEN'])

