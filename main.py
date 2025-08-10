import os
import discord
from discord.ext import commands
from discord.ui import Button, View

# ===== 환경변수에서 토큰 불러오기 =====
TOKEN = os.getenv("BOT_TOKEN")

# ===== 설정 =====
GUILD_ID = 1398256208887939214  # 서버 ID
CHANNEL_ID = 1401731162111610890  # 배너를 보낼 채널 ID
ROLE_ID = 1401917813601599580    # 지급/제거할 역할 ID
MESSAGE_ID_FILE = "banner_message_id.txt"  # 메시지 ID 저장 파일

# 인텐트 설정
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


# ===== 버튼 뷰 =====
class BannerView(View):
    def __init__(self):
        super().__init__(timeout=None)  # 무제한 유지
        button1 = Button(label="파트너 표시", style=discord.ButtonStyle.green, row=0)
        button2 = Button(label="파트너 가리기", style=discord.ButtonStyle.red, row=0)

        async def button1_callback(interaction):
            role = interaction.guild.get_role(ROLE_ID)
            if not role:
                await interaction.response.send_message("❌ 역할을 찾을 수 없습니다.", ephemeral=True)
                return
            if role in interaction.user.roles:
                await interaction.response.send_message("⚠ 이미 이 역할이 있습니다!", ephemeral=True)
                return
            await interaction.user.add_roles(role)
            await interaction.response.send_message("✅ 역할 지급 완료!", ephemeral=True)

        async def button2_callback(interaction):
            role = interaction.guild.get_role(ROLE_ID)
            if not role:
                await interaction.response.send_message("❌ 역할을 찾을 수 없습니다.", ephemeral=True)
                return
            if role not in interaction.user.roles:
                await interaction.response.send_message("⚠ 이 역할이 없습니다!", ephemeral=True)
                return
            await interaction.user.remove_roles(role)
            await interaction.response.send_message("❌ 역할 제거 완료!", ephemeral=True)

        button1.callback = button1_callback
        button2.callback = button2_callback
        self.add_item(button1)
        self.add_item(button2)


# ===== 봇 시작 이벤트 =====
@bot.event
async def on_ready():
    print(f"✅ 로그인됨: {bot.user}")
    try:
        with open(MESSAGE_ID_FILE, "r") as f:
            message_id = int(f.read().strip())
        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            await channel.fetch_message(message_id)
            bot.add_view(BannerView())
            print("🔄 버튼 복구 완료")
    except FileNotFoundError:
        print("⚠ 저장된 메시지 ID 없음. !배너 명령어로 생성하세요.")


# ===== 명령어 =====
@bot.command()
async def 배너(ctx):
    embed = discord.Embed(
        title="🔔 파트너 채널 확인",
        description="버튼을 클릭하면 역할이 지급되거나 제거됩니다.",
        color=0x000000
    )

    view = BannerView()
    msg = await ctx.send(embed=embed, view=view)

    with open(MESSAGE_ID_FILE, "w") as f:
        f.write(str(msg.id))

    await ctx.send("✅ 배너 생성 완료. 봇이 꺼져도 버튼이 유지됩니다.")


# ===== 실행 =====
if TOKEN is None:
    print("❌ BOT_TOKEN 환경변수가 설정되지 않았습니다.")
else:
    bot.run(TOKEN)
