# CODE MODE
import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv

# Tải cấu hình từ file .env
load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)

# --- PHẦN 1: ĐỊNH NGHĨA GIAO DIỆN MENU ---
class MenuQuanLyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        placeholder="Chọn chức năng quản lý...",
        options=[
            discord.SelectOption(label="Ghim tin nhắn", description="Cách dùng lệnh /ghim", emoji="📌"),
            discord.SelectOption(label="Tự động xoá tin nhắn", description="Cách dùng lệnh /autodel", emoji="🧹"),
            discord.SelectOption(label="Xem thông tin Bot", description="Kiểm tra trạng thái hệ thống", emoji="🤖")
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        if select.values[0] == "Ghim tin nhắn":
            embed = discord.Embed(
                title="📌 Hướng dẫn Lệnh /ghim",
                description="Dùng để ghim các nội dung quan trọng lên đầu kênh chat.",
                color=discord.Color.blue()
            )
            embed.add_field(name="Cách 1: Ghim văn bản mới", value="`/ghim <Nội dung cần ghim>`", inline=False)
            embed.add_field(name="Cách 2: Ghim tin nhắn cũ", value="Phản hồi (Reply) lại tin nhắn đó và gõ `/ghim`", inline=False)
            await interaction.response.send_message(embed=embed, ephemeral=True)

        elif select.values[0] == "Tự động xoá tin nhắn":
            embed = discord.Embed(
                title="🧹 Hướng dẫn Lệnh /autodel",
                description="Tự động quét và xoá tin nhắn sau một khoảng thời gian thiết lập.",
                color=discord.Color.red()
            )
            embed.add_field(name="Cú pháp", value="`/autodel <#tên-kênh> <số-giây> <all/people>`", inline=False)
            embed.add_field(name="Giải thích chế độ", value="• `all`: Xoá tất cả (cả người và bot).\n• `people`: Chỉ xoá tin nhắn của người dùng (giữ lại bot).", inline=False)
            await interaction.response.send_message(embed=embed, ephemeral=True)

        elif select.values[0] == "Xem thông tin Bot":
            latency = round(bot.latency * 1000)
            embed = discord.Embed(
                title="🤖 Trạng thái Hệ thống",
                description=f"Bot đang hoạt động ổn định.\n• **Độ trễ:** {latency}ms\n• **Prefix:** `/`",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

# --- PHẦN 2: CÁC SỰ KIỆN VÀ LỆNH CỦA BOT ---
@bot.event
async def on_ready():
    print(f'Bot {bot.user.name} đã sẵn sàng hoạt động!')

@bot.command(name='menu')
@commands.has_permissions(manage_messages=True)
async def menu(ctx):
    embed = discord.Embed(
        title="🛠️ BẢNG ĐIỀU KHIỂN QUẢN LÝ",
        description="Vui lòng chọn danh mục phía dưới để xem hướng dẫn chi tiết từng lệnh.",
        color=discord.Color.blurple()
    )
    await ctx.send(embed=embed, view=MenuQuanLyView())
    try: await ctx.message.delete()
    except: pass

@bot.command(name='ghim')
@commands.has_permissions(manage_messages=True)
async def ghim(ctx, *, content: str = None):
    if ctx.message.reference:
        msg_to_pin = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        await msg_to_pin.pin()
        await ctx.send("📌 Đã ghim tin nhắn thành công!", delete_after=5)
    elif content:
        msg = await ctx.send(f"📌 **Thông báo được ghim:**\n{content}")
        await msg.pin()
    else:
        await ctx.send("Vui lòng reply một tin nhắn hoặc nhập nội dung sau lệnh `/ghim`.", delete_after=5)
    try: await ctx.message.delete()
    except: pass

@bot.command(name='autodel')
@commands.has_permissions(manage_messages=True)
async def autodel(ctx, channel: discord.TextChannel, time: int, mode: str):
    mode = mode.lower()
    if mode not in ['all', 'people']:
        await ctx.send("Chế độ không hợp lệ! Chọn `all` hoặc `people`.", delete_after=5)
        return

    await ctx.send(f"⏳ Sẽ xoá tự động trên kênh {channel.mention} sau {time} giây...", delete_after=10)
    await asyncio.sleep(time)

    def check_msg(message):
        return True if mode == 'all' else not message.author.bot

    try:
        deleted = await channel.purge(limit=500, check=check_msg)
        await ctx.send(f"🧹 Đã tự động xoá `{len(deleted)}` tin nhắn tại kênh {channel.mention}.", delete_after=10)
    except discord.Forbidden:
        await ctx.send("Bot thiếu quyền `Manage Messages`.", delete_after=10)
    except Exception as e:
        await ctx.send(f"Lỗi: {e}", delete_after=10)

@menu.error
@ghim.error
@autodel.error
async def permission_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("Bạn không có quyền `Manage Messages` để dùng lệnh này!", delete_after=5)

# Chạy bot bằng token lấy từ file .env
TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)
