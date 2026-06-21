# CODE MODE
import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot {bot.user.name} đã sẵn sàng quản lý!')

# Lệnh /ghim: Ghim tin nhắn được reply hoặc ghim nội dung text phía sau
@bot.command(name='ghim')
@commands.has_permissions(manage_messages=True)
async def ghim(ctx, *, content: str = None):
    # Nếu người dùng reply một tin nhắn khác
    if ctx.message.reference:
        msg_to_pin = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        await msg_to_pin.pin()
        await ctx.send("📌 Đã ghim tin nhắn thành công!", delete_after=5)
    # Nếu người dùng nhập text sau lệnh /ghim
    elif content:
        msg = await ctx.send(f"📌 **Thông báo được ghim:**\n{content}")
        await msg.pin()
    else:
        await ctx.send("Vui lòng reply một tin nhắn hoặc nhập nội dung cần ghim sau lệnh `/ghim`.", delete_after=5)
    
    # Xoá lệnh gốc của người dùng cho sạch kênh
    try:
        await ctx.message.delete()
    except:
        pass

# Lệnh /autodel (channel) (time) (all/people)
@bot.command(name='autodel')
@commands.has_permissions(manage_messages=True)
async def autodel(ctx, channel: discord.TextChannel, time: int, mode: str):
    mode = mode.lower()
    if mode not in ['all', 'people']:
        await ctx.send("Chế độ (mode) không hợp lệ! Vui lòng chọn `all` (tất cả bao gồm cả bot) hoặc `people` (chỉ người dùng, trừ bot).", delete_after=5)
        return

    await ctx.send(f"⏳ Hệ thống bắt đầu quét và xoá tự động trên kênh {channel.mention} sau {time} giây...", delete_after=10)

    # Đợi số giây được chỉ định
    await asyncio.sleep(time)

    # Hàm lọc tin nhắn dựa theo chế độ
    def check_msg(message):
        if mode == 'all':
            return True
        elif mode == 'people':
            return not message.author.bot
        return False

    try:
        # Xoá tin nhắn hàng loạt bằng purge (giới hạn tối đa 500 tin trong 1 lần quét)
        deleted = await channel.purge(limit=500, check=check_msg)
        await ctx.send(f"🧹 Đã tự động xoá thành công `{len(deleted)}` tin nhắn (Chế độ: `{mode}`) tại kênh {channel.mention}.", delete_after=10)
    except discord.Forbidden:
        await ctx.send("Bot thiếu quyền `Manage Messages` (Quản lý tin nhắn) để thực hiện thao tác này.", delete_after=10)
    except Exception as e:
        await ctx.send(f"Đã xảy ra lỗi khi xoá tin nhắn: {e}", delete_after=10)

# Bắt lỗi nếu người dùng thiếu quyền khi dùng lệnh
@ghim.error
@autodel.error
async def permission_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("Bạn không có quyền `Manage Messages` để sử dụng lệnh quản lý này!", delete_after=5)

TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)
      
