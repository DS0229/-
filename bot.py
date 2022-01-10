import discord, sqlite3, setting
from discord_buttons_plugin import ButtonType
from discord_components import DiscordComponents, ComponentsBot, Select, SelectOption, Button, ButtonStyle, ActionRow

client = discord.Client()

@client.event
async def on_ready():
    DiscordComponents(client)

@client.event
async def on_message(message):
    if message.content.startswith("!초대지정 "):
        if message.author.guild_permissions.administrator or message.author.id in int(setting.admin_id):
            if not isinstance(message.channel, discord.channel.DMChannel):
                server_id = message.content.split(" ")[1]
                if server_id.isdigit():
                    con = sqlite3.connect("DB.db")
                    cur = con.cursor()
                    cur.execute("SELECT * FROM info WHERE serverid == ?;", (server_id,))
                    info = cur.fetchone()
                    con.close()
                    if info != None:
                        con = sqlite3.connect("DB.db")
                        cur = con.cursor()
                        cur.execute("UPDATE info SET channelid = ? WHERE serverid == ?;", (message.channel.id, server_id))
                        con.commit()
                        con.close()
                    else:
                        con = sqlite3.connect("DB.db")
                        cur = con.cursor()
                        cur.execute("INSERT INTO info VALUES(?, ?);", (server_id, message.channel.id))
                        con.commit()
                        con.close()
                    await message.channel.send(embed=discord.Embed(title="지정 성공", description="지정이 성공적으로 완료되었습니다.", color=0x4461ff))
                else:
                    await message.channel.send(embed=discord.Embed(title="지정 실패", description="올바른 서버 아이디를 입력해주세요.", color=0x4461ff))

    if message.content == "!도움말":
        if not isinstance(message.channel, discord.channel.DMChannel):
            await message.channel.send(embed=discord.Embed(title="도움말", description="!초대지정: 초대를 원하는 서버에 `!초대지정 (인증을 할 서버의 아이디)`\n!메시지: 인증 메시지 전송", color=0x4461ff))

    if message.content == "!메시지":
        if message.author.guild_permissions.administrator or message.author.id in int(setting.admin_id):
            if not isinstance(message.channel, discord.channel.DMChannel):
                con = sqlite3.connect("DB.db")
                cur = con.cursor()
                cur.execute("SELECT * FROM info WHERE serverid == ?;", (message.guild.id,))
                info = cur.fetchone()
                con.close()
                if info != None:
                    await message.channel.send(
                        embed=discord.Embed(title="서버 참가하기", description="서버에 참가하시려면 아래 인증 버튼을 클릭해주세요.", color=0x4461ff),
                        components = [
                            ActionRow(
                                Button(style=ButtonStyle.blue,label = "인증",custom_id="인증")
                            )
                        ]
                    )
                else:
                    await message.channel.send(embed=discord.Embed(title="메시지 전송 실패", description="일치하는 서버 아이디가 없습니다.\n초대를 원하는 서버에 `!초대지정 (인증을 할 서버의 아이디)` 라고 입력한 후에 다시 시도해주세요.", color=0x4461ff))

@client.event
async def on_button_click(interaction):
    con = sqlite3.connect("DB.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM info WHERE serverid == ?;", (interaction.guild.id,))
    info = cur.fetchone()
    con.close()
    if info != None:
        if interaction.custom_id == "인증":
            try:
                link = await client.get_channel(info[1]).create_invite(max_age=60, max_uses=1)
                await interaction.respond(embed=discord.Embed(description="Made by. https://discord.gg/fastdm", color=0x4461ff), content=str(link))
            except:
                await interaction.respond(embed=discord.Embed(title="인증 실패", description="서버에 봇이 있는지 봇한테 초대링크를 생성할 권한이 있는지 확인해주세요.", color=0x4461ff))

client.run(setting.token)
