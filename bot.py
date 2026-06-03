import discord
import os
from discord.ext import commands
from dotenv import load_dotenv

TOKEN = "MTUxMTU1NzEwODM1MTUwMDQwOQ.GyJ573.ADFVQbPPkWnz2jDZujr1p5IcN5YMEHv81xVGM0"
HENRIK_KEY = "MTUxMTU1NzEwODM1MTUwMDQwOQ.Gv5L30.a1Kg-vMg8ylvBgEBa3nRZdQrnbzbBg40gU9hWk"

# Configuração básica do bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Quando o bot ligar
@bot.event
async def on_ready():
    print(f"Bot ligado! Logado como {bot.user}")

# Comando de ping (pra testar se tá funcionando)
@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong! Bot funcionando!")

import random

perguntas_todas = [
    {"pergunta": "Qual agente usa a habilidade Paranoia?", "resposta": "omen"},
    {"pergunta": "Quantos agentes existiam no lançamento do Valorant?", "resposta": "11"},
    {"pergunta": "Qual agente pode se tornar invisível?", "resposta": "yoru"},
    {"pergunta": "Qual é o nome da organização vilã do Valorant?", "resposta": "kingdom"},
    {"pergunta": "Qual agente usa câmeras de vigilância?", "resposta": "cypher"},
    {"pergunta": "Qual agente vem do Brasil?", "resposta": "raze"},
    {"pergunta": "Qual agente pode ressuscitar aliados?", "resposta": "sage"},
    {"pergunta": "Qual agente usa um arco e flecha?", "resposta": "sova"},
    {"pergunta": "Qual é o nome da ultimate da Raze?", "resposta": "showstopper"},
    {"pergunta": "Quantos jogadores tem cada time no Valorant?", "resposta": "5"},
    {"pergunta": "Qual agente usa fogo nas habilidades?", "resposta": "phoenix"},
    {"pergunta": "Qual agente controla estrelas no mapa?", "resposta": "astra"},
    {"pergunta": "Qual agente tem uma habilidade chamada Curar?", "resposta": "sage"},
    {"pergunta": "Qual agente vem da Coreia do Sul?", "resposta": "sage"},
    {"pergunta": "Qual mapa tem dois portais de teletransporte?", "resposta": "bind"},
    {"pergunta": "Qual agente usa uma mochila de foguetes?", "resposta": "raze"},
    {"pergunta": "Qual é o nome do mapa ambientado em Marrocos?", "resposta": "bind"},
    {"pergunta": "Qual agente pode duplicar a si mesmo?", "resposta": "mirror"},
    {"pergunta": "Qual agente usa veneno nas habilidades?", "resposta": "viper"},
    {"pergunta": "Qual mapa fica na Índia?", "resposta": "pearl"},
    {"pergunta": "Qual agente tem uma habilidade chamada Blade Storm?", "resposta": "jett"},
    {"pergunta": "Qual agente vem da Alemanha?", "resposta": "killjoy"},
    {"pergunta": "Qual agente instala torretas e minas?", "resposta": "killjoy"},
    {"pergunta": "Qual é o nome da ultimate do Omen?", "resposta": "from the shadows"},
    {"pergunta": "Qual agente usa habilidades de gelo?", "resposta": "sage"},
    {"pergunta": "Quantos rounds vence quem ganhar a partida normal?", "resposta": "13"},
    {"pergunta": "Qual agente vem da China?", "resposta": "sage"},
    {"pergunta": "Qual é o nome da ultimate da Jett?", "resposta": "blade storm"},
    {"pergunta": "Qual mapa foi adicionado em 2022 e fica debaixo d'água?", "resposta": "pearl"},
    {"pergunta": "Qual agente usa um escudo de barreira?", "resposta": "sage"},
]

# Guarda quais perguntas já foram usadas por servidor
perguntas_usadas = {}

@bot.command()
async def quiz(ctx):
    guild_id = str(ctx.guild.id)

    # Se já usou todas, reseta
    if guild_id not in perguntas_usadas:
        perguntas_usadas[guild_id] = []

    disponiveis = [p for p in perguntas_todas if p not in perguntas_usadas[guild_id]]

    if not disponiveis:
        perguntas_usadas[guild_id] = []
        disponiveis = perguntas_todas.copy()
        await ctx.send("🔄 Todas as perguntas foram usadas! Reiniciando o banco de perguntas...")

    escolha = random.choice(disponiveis)
    perguntas_usadas[guild_id].append(escolha)

    embed = discord.Embed(
        title="🎯 Quiz Valorant!",
        description=escolha["pergunta"],
        color=0xFF4655
    )
    embed.set_footer(text=f"Você tem 30 segundos • {len(disponiveis)-1} perguntas restantes")
    await ctx.send(embed=embed)

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        resposta = await bot.wait_for("message", check=check, timeout=30)

        if resposta.content.lower() == escolha["resposta"]:
            embed_ok = discord.Embed(
                title="✅ Correto!",
                description=f"Parabéns {ctx.author.name}! +15 XP",
                color=0x00FF88
            )
            # Bonus de XP por acertar o quiz
            dados = carregar_xp()
            user_id = str(ctx.author.id)
            if user_id in dados:
                dados[user_id]["xp"] += 15
                salvar_xp(dados)
            await ctx.send(embed=embed_ok)
        else:
            embed_err = discord.Embed(
                title="❌ Errado!",
                description=f"A resposta era: **{escolha['resposta']}**",
                color=0xFF4655
            )
            await ctx.send(embed=embed_err)

    except:
        await ctx.send("⏰ Tempo esgotado!")

import json
import os

# Carrega ou cria o arquivo de XP
def carregar_xp():
    if os.path.exists("xp.json"):
        with open("xp.json", "r") as f:
            return json.load(f)
    return {}

def salvar_xp(dados):
    with open("xp.json", "w") as f:
        json.dump(dados, f)

# Ganha XP automaticamente ao mandar mensagem
@bot.event
async def on_message(message):
    if message.author.bot:
        return  # Ignora mensagens de outros bots

    dados = carregar_xp()
    user_id = str(message.author.id)

    if user_id not in dados:
        dados[user_id] = {"xp": 0, "nivel": 1}

    dados[user_id]["xp"] += 10  # Ganha 10 XP por mensagem

    # Sobe de nível a cada 100 XP
    xp_atual = dados[user_id]["xp"]
    nivel_novo = (xp_atual // 100) + 1

    if nivel_novo > dados[user_id]["nivel"]:
        dados[user_id]["nivel"] = nivel_novo
        await message.channel.send(
            f"🎉 Parabéns {message.author.name}! Você subiu para o nível **{nivel_novo}**!"
        )

    salvar_xp(dados)
    await bot.process_commands(message)  # Importante pra os outros comandos continuarem funcionando

# Comando pra ver seu XP
@bot.command()
async def rank(ctx):
    dados = carregar_xp()
    user_id = str(ctx.author.id)

    if user_id not in dados:
        await ctx.send("Você ainda não tem XP! Manda uma mensagem pra começar.")
        return

    xp = dados[user_id]["xp"]
    nivel = dados[user_id]["nivel"]
    proximo = nivel * 100
    barra = int((xp % 100) / 10)  # Barra de progresso de 0 a 10
    progresso = "█" * barra + "░" * (10 - barra)

    embed = discord.Embed(
        title=f"📊 Ranking de {ctx.author.name}",
        color=0xFF4655  # Vermelho do Valorant
    )
    embed.add_field(name="Nível", value=f"**{nivel}**", inline=True)
    embed.add_field(name="XP", value=f"**{xp}/{proximo}**", inline=True)
    embed.add_field(name="Progresso", value=f"`{progresso}`", inline=False)
    embed.set_thumbnail(url=ctx.author.avatar.url)
    embed.set_footer(text="ValBot • Sistema de Ranking")

    await ctx.send(embed=embed)


# Comando pra ver o top 5 do servidor
@bot.command()
async def top(ctx):
    dados = carregar_xp()

    if not dados:
        await ctx.send("Ninguém tem XP ainda!")
        return

    ranking = sorted(dados.items(), key=lambda x: x[1]["xp"], reverse=True)[:5]

    embed = discord.Embed(
        title="🏆 Top 5 do Servidor",
        color=0xFF4655
    )

    medalhas = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]

    for i, (user_id, info) in enumerate(ranking):
        usuario = await bot.fetch_user(int(user_id))
        embed.add_field(
            name=f"{medalhas[i]} {usuario.name}",
            value=f"Nível {info['nivel']} • {info['xp']} XP",
            inline=False
        )

    embed.set_footer(text="ValBot • Sistema de Ranking")
    await ctx.send(embed=embed)


import asyncio

@bot.command()
async def sorteio(ctx, tempo: int, *, premio: str):
    """Uso: !sorteio 60 Skin do Vandal"""
    
    embed = discord.Embed(
        title="🎁 SORTEIO!",
        description=f"**Prêmio:** {premio}\n\nReaja com 🎉 para participar!\nTempo: **{tempo} segundos**",
        color=0xFF4655
    )
    embed.set_footer(text=f"Sorteio criado por {ctx.author.name}")
    
    mensagem = await ctx.send(embed=embed)
    await mensagem.add_reaction("🎉")
    
    # Espera o tempo definido
    await asyncio.sleep(tempo)
    
    # Busca quem reagiu
    mensagem = await ctx.channel.fetch_message(mensagem.id)
    usuarios = []
    
    for reacao in mensagem.reactions:
        if str(reacao.emoji) == "🎉":
            async for usuario in reacao.users():
                if not usuario.bot:
                    usuarios.append(usuario)
    
    # Sorteia o vencedor
    if not usuarios:
        await ctx.send("❌ Ninguém participou do sorteio!")
        return
    
    vencedor = random.choice(usuarios)
    
    embed_resultado = discord.Embed(
        title="🏆 Resultado do Sorteio!",
        description=f"Parabéns {vencedor.mention}!\nVocê ganhou **{premio}**! 🎉",
        color=0xFF4655
    )
    
    await ctx.send(embed=embed_resultado)


@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Game(name="!quiz | Valorant Bot")
    )
    print(f"Bot ligado! Logado como {bot.user}")


import aiohttp

HENRIK_KEY = "HDEV-25f4cd0a-3f20-46e4-ad4b-34538f3c492b"  # Substitui pela sua chave

@bot.command()
async def stats(ctx, *, nome: str):
    if "#" not in nome:
        await ctx.send("❌ Use o formato correto: `!stats Nome#TAG`")
        return

    partes = nome.split("#")
    player_name = partes[0]
    player_tag = partes[1]

    msg = await ctx.send("🔍 Buscando stats...")

    try:
        async with aiohttp.ClientSession() as session:

            url = f"https://api.henrikdev.xyz/valorant/v2/account/{player_name}/{player_tag}"
            headers = {"Authorization": HENRIK_KEY}

            async with session.get(url, headers=headers) as resp:
                if resp.status != 200:
                    await msg.edit(content="❌ Jogador não encontrado! Verifique o nome e a TAG.")
                    return
                perfil = await resp.json()

            regiao = perfil["data"]["region"]
            url_rank = f"https://api.henrikdev.xyz/valorant/v3/mmr/{regiao}/pc/{player_name}/{player_tag}"

            async with session.get(url_rank, headers=headers) as resp2:
                rank_data = await resp2.json()

        dados = perfil["data"]
        rank_info = rank_data.get("data", {})

        nivel = dados.get("account_level", "?")
        rank_atual = rank_info.get("current", {}).get("tier", {}).get("name", "Sem rank")
        elo = rank_info.get("current", {}).get("elo", 0)
        rr = rank_info.get("current", {}).get("rr", 0)

        # Barra de RR (0 a 100)
        barra_rr = int(rr / 10)
        progresso = "█" * barra_rr + "░" * (10 - barra_rr)

        # Cor muda conforme o rank
        cores = {
            "Iron": 0x8B8B8B,
            "Bronze": 0xCD7F32,
            "Silver": 0xC0C0C0,
            "Gold": 0xFFD700,
            "Platinum": 0x00CED1,
            "Diamond": 0xB9F2FF,
            "Ascendant": 0x00FF88,
            "Immortal": 0xFF4655,
            "Radiant": 0xFFE066,
        }
        cor = 0xFF4655  # padrão vermelho
        for rank_nome, rank_cor in cores.items():
            if rank_nome in rank_atual:
                cor = rank_cor
                break

        embed = discord.Embed(
            title=f"🎮  {player_name}#{player_tag}",
            color=cor
        )
        embed.add_field(
            name="🏆 Rank Atual",
            value=f"**{rank_atual}**",
            inline=True
        )
        embed.add_field(
            name="⭐ ELO",
            value=f"**{elo}**",
            inline=True
        )
        embed.add_field(
            name="🎯 RR",
            value=f"**{rr}/100**",
            inline=True
        )
        embed.add_field(
            name="📈 Progresso do RR",
            value=f"`{progresso}` {rr}%",
            inline=False
        )
        embed.add_field(
            name="🎮 Nível da Conta",
            value=f"**{nivel}**",
            inline=True
        )
        embed.add_field(
            name="🌎 Região",
            value=f"**{regiao.upper()}**",
            inline=True
        )
        embed.set_footer(text="ValBot • Powered by Henrik API")

        await msg.delete()
        await ctx.send(embed=embed)

    except Exception as e:
        await msg.edit(content="❌ Erro ao buscar stats. Tente novamente.")

@bot.command()
async def historico(ctx, *, nome: str):
    """Uso: !historico NomeDoJogador#TAG"""

    if "#" not in nome:
        await ctx.send("❌ Use o formato correto: `!historico Nome#TAG`")
        return

    partes = nome.split("#")
    player_name = partes[0]
    player_tag = partes[1]

    msg = await ctx.send("🔍 Buscando histórico...")

    try:
        async with aiohttp.ClientSession() as session:

            # Busca região primeiro
            url = f"https://api.henrikdev.xyz/valorant/v2/account/{player_name}/{player_tag}"
            headers = {"Authorization": HENRIK_KEY}

            async with session.get(url, headers=headers) as resp:
                if resp.status != 200:
                    await msg.edit(content="❌ Jogador não encontrado!")
                    return
                perfil = await resp.json()

            regiao = perfil["data"]["region"]

            # Busca últimas partidas
            url_matches = f"https://api.henrikdev.xyz/valorant/v4/matches/{regiao}/pc/{player_name}/{player_tag}?mode=competitive&size=5"

            async with session.get(url_matches, headers=headers) as resp2:
                matches_data = await resp2.json()

        partidas = matches_data.get("data", [])

        if not partidas:
            await msg.edit(content="❌ Nenhuma partida encontrada!")
            return

        embed = discord.Embed(
            title=f"📜 Histórico de {player_name}#{player_tag}",
            description="Últimas 5 partidas competitivas",
            color=0xFF4655
        )

        for partida in partidas:
            # Acha o jogador na partida
            jogador = None
            for p in partida["players"]:
                if p["name"].lower() == player_name.lower() and p["tag"].lower() == player_tag.lower():
                    jogador = p
                    break

            if not jogador:
                continue

            mapa = partida["metadata"]["map"]["name"]
            resultado_time = jogador["team_id"]

            # Verifica se ganhou
            times = partida.get("teams", [])
            ganhou = False
            for time in times:
                if time["team_id"] == resultado_time and time["won"]:
                    ganhou = True
                    break

            resultado = "✅ Vitória" if ganhou else "❌ Derrota"

            # Stats do jogador
            stats = jogador.get("stats", {})
            kills = stats.get("kills", 0)
            deaths = stats.get("deaths", 1)
            assists = stats.get("assists", 0)
            kda = round(kills / deaths, 2)
            agente = jogador.get("agent", {}).get("name", "?")

            embed.add_field(
                name=f"{resultado} — {mapa}",
                value=f"Agente: **{agente}** • K/D/A: **{kills}/{deaths}/{assists}** • KDA: **{kda}**",
                inline=False
            )

        embed.set_footer(text="ValBot • Powered by Henrik API")
        await msg.delete()
        await ctx.send(embed=embed)

    except Exception as e:
        await msg.edit(content="❌ Erro ao buscar histórico. Tente novamente.")
# Inicia o bot
bot.run(TOKEN)