import discord
import os
import json
import random
import asyncio
import aiohttp
from datetime import datetime, timedelta
from discord.ext import commands, tasks
from dotenv import load_dotenv
from auth import servidor_autorizado, status_servidor, carregar_autorizados, carregar_testes, salvar_testes
from perguntas import perguntas_todas

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
HENRIK_KEY = os.getenv("HENRIK_KEY", "")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

SEU_ID = "1511753229480755356"
COR_PADRAO = 0xFF4655
VERSAO = "2.0"

# ============================================================
# HELPERS – arquivos JSON
# ============================================================
def carregar_json(arquivo, padrao):
    if os.path.exists(arquivo):
        try:
            with open(arquivo, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return padrao
    return padrao

def salvar_json(arquivo, dados):
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)

def carregar_xp(): return carregar_json("xp.json", {})
def salvar_xp(d): salvar_json("xp.json", d)
def carregar_perfis(): return carregar_json("perfis.json", {})
def salvar_perfis(d): salvar_json("perfis.json", d)
def carregar_times(): return carregar_json("times.json", {})
def salvar_times(d): salvar_json("times.json", d)
def carregar_conquistas(): return carregar_json("conquistas.json", {})
def salvar_conquistas(d): salvar_json("conquistas.json", d)
def carregar_stats(): return carregar_json("stats.json", {})
def salvar_stats(d): salvar_json("stats.json", d)
def carregar_patch(): return carregar_json("patch_notes.json", [])

# ============================================================
# HELPERS – visuais
# ============================================================
CORES_RANK = {
    "Iron": 0x4D4D4D, "Bronze": 0xCD7F32, "Silver": 0xC0C0C0,
    "Gold": 0xFFD700, "Platinum": 0x00CED1, "Diamond": 0xB9F2FF,
    "Ascendant": 0x00FF88, "Immortal": 0xFF4655, "Radiant": 0xFFE066,
}

# URLs de portrait de agentes da valorant-api.com (displayicon)
AGENT_IMAGES = {
    "jett": "https://media.valorant-api.com/agents/add6443a-41bd-e414-f6ad-e58d267f4e95/displayicon.png",
    "phoenix": "https://media.valorant-api.com/agents/eb93336a-449b-9c1b-0a54-a891f7921d69/displayicon.png",
    "sage": "https://media.valorant-api.com/agents/569fdd95-4d10-43ab-ca70-79becc718b46/displayicon.png",
    "sova": "https://media.valorant-api.com/agents/ded3520f-4264-bfed-162d-b080e2abccf9/displayicon.png",
    "viper": "https://media.valorant-api.com/agents/707eab51-4836-f488-046a-cda6bf494859/displayicon.png",
    "cypher": "https://media.valorant-api.com/agents/117ed9e3-49f3-6512-3ccf-0cada7e3823b/displayicon.png",
    "reyna": "https://media.valorant-api.com/agents/a3bfb853-43b2-7238-a4f1-ad90e9e46bcc/displayicon.png",
    "killjoy": "https://media.valorant-api.com/agents/1e58de9c-4950-5125-93e9-a0aee9f98746/displayicon.png",
    "breach": "https://media.valorant-api.com/agents/5f8d3a7f-467b-97f3-062c-13acf203c006/displayicon.png",
    "omen": "https://media.valorant-api.com/agents/8e253930-4c05-31dd-1b6c-968525494517/displayicon.png",
    "brimstone": "https://media.valorant-api.com/agents/9f0d8ba9-4140-b941-57d3-a7ad57c6b417/displayicon.png",
    "raze": "https://media.valorant-api.com/agents/f94c3b30-42be-e959-889c-5aa313dba261/displayicon.png",
    "skye": "https://media.valorant-api.com/agents/6f2a04ca-43e0-be17-7f36-b3908627744d/displayicon.png",
    "yoru": "https://media.valorant-api.com/agents/7f94d92c-4234-0a36-9646-3a87eb8b5c89/displayicon.png",
    "astra": "https://media.valorant-api.com/agents/41fb69c1-4189-7b37-f117-bcaf1e96f1bf/displayicon.png",
    "kay/o": "https://media.valorant-api.com/agents/601dbbe7-43ce-be57-2a40-4abd24953621/displayicon.png",
    "chamber": "https://media.valorant-api.com/agents/22697a3d-45bf-8dd7-4fec-84a9e28c69d7/displayicon.png",
    "neon": "https://media.valorant-api.com/agents/bb2a4828-46eb-8cd1-e765-15848195d751/displayicon.png",
    "fade": "https://media.valorant-api.com/agents/dade69b4-4f5a-8528-247b-219e5a1facd6/displayicon.png",
    "harbor": "https://media.valorant-api.com/agents/95b78ed7-4637-86d9-7e41-71ba8c293152/displayicon.png",
    "gekko": "https://media.valorant-api.com/agents/e370fa57-4757-3604-3648-499e1f642d3f/displayicon.png",
    "deadlock": "https://media.valorant-api.com/agents/cc8b64c8-4b25-4ff9-6e7f-37b4da43d235/displayicon.png",
    "iso": "https://media.valorant-api.com/agents/0e38b510-41a8-5780-5e8f-568b2a4f2d6c/displayicon.png",
    "clove": "https://media.valorant-api.com/agents/1dbf2edd-7729-4540-b09c-c0a3b9aa20a4/displayicon.png",
    "vyse": "https://media.valorant-api.com/agents/efba5359-4016-a1e5-7626-b1ae76895940/displayicon.png",
    "tejo": "https://media.valorant-api.com/agents/b444168c-4e35-8076-db47-ef9bf368f384/displayicon.png",
    "waylay": "https://media.valorant-api.com/agents/df1cb487-4902-002e-5c17-d28e83e78588/displayicon.png",
}

def get_agent_image(nome):
    if not nome:
        return None
    return AGENT_IMAGES.get(nome.lower())

def cor_por_rank(rank_atual):
    if not rank_atual:
        return COR_PADRAO
    for nome, cor in CORES_RANK.items():
        if nome.lower() in rank_atual.lower():
            return cor
    return COR_PADRAO

def barra_progresso(atual, total, tamanho=15):
    """Barra estilizada com blocos cheios e vazios"""
    if total <= 0:
        return "░" * tamanho
    proporcao = max(0, min(1, atual / total))
    cheios = int(proporcao * tamanho)
    vazios = tamanho - cheios
    return "▰" * cheios + "▱" * vazios

# ============================================================
# AUTORIZAÇÃO – decorator individual por comando
# ============================================================
SERVIDORES_GRATUITOS_BOT = ["1511754478913720410"]  # Arca Oficial

def requer_acesso():
    async def predicate(ctx):
        autorizados = carregar_autorizados()
        if str(ctx.guild.id) in SERVIDORES_GRATUITOS_BOT or str(ctx.guild.id) in autorizados:
            return True
        st = status_servidor(ctx.guild.id)
        if st == "expirado":
            await ctx.send("❌ Seu período de teste de 3 dias encerrou. Para continuar usando o ValBot acesse: https://discord.gg/VKHG6MFh")
        else:
            await ctx.send("⚠️ Este servidor não tem acesso ao ValBot. Entre em contato: https://discord.gg/VKHG6MFh")
        return False
    return commands.check(predicate)

@tasks.loop(minutes=60)
async def verificar_testes_expirando():
    """A cada hora verifica se algum servidor em teste está a menos de 24h do fim."""
    from datetime import datetime, timezone
    testes = carregar_testes()
    alterado = False
    for sid, info in testes.items():
        if info.get("aviso_enviado"):
            continue
        inicio = datetime.fromisoformat(info["inicio"])
        if inicio.tzinfo is None:
            inicio = inicio.replace(tzinfo=timezone.utc)
        horas = (datetime.now(timezone.utc) - inicio).total_seconds() / 3600
        if horas >= 48:  # passaram 48h → faltam menos de 24h
            guild = bot.get_guild(int(sid))
            if guild:
                canal = next(
                    (c for c in guild.text_channels
                     if c.permissions_for(guild.me).send_messages),
                    None
                )
                if canal:
                    await canal.send(
                        "⏰ Seu período de teste do ValBot está acabando! Faltam menos de 24h. "
                        "Para continuar com acesso entre em contato: https://discord.gg/VKHG6MFh"
                    )
            testes[sid]["aviso_enviado"] = True
            alterado = True
    if alterado:
        salvar_testes(testes)

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name=f"!ajuda | ValBot v{VERSAO}"))
    print(f"Bot ligado! Logado como {bot.user} | v{VERSAO}")
    print(f"Henrik Key carregada: {HENRIK_KEY[:15]}...")
    if not verificar_testes_expirando.is_running():
        verificar_testes_expirando.start()

@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong! Bot funcionando!")

# ============================================================
# CONQUISTAS – definição e verificação
# ============================================================
CONQUISTAS = {
    "primeiro_passo":    {"nome": "🌱 Primeiro Passo",   "desc": "Mandar primeira mensagem",                 "dif": "Fácil"},
    "atirador_elite":    {"nome": "🎯 Atirador de Elite", "desc": "Acertar 10 perguntas do quiz",             "dif": "Fácil"},
    "comunicador":       {"nome": "💬 Comunicador",       "desc": "Mandar 100 mensagens",                     "dif": "Fácil"},
    "bem_vindo_time":    {"nome": "🤝 Bem Vindo ao Time", "desc": "Entrar em um time",                        "dif": "Fácil"},
    "escalando":         {"nome": "🏆 Escalando",         "desc": "Chegar ao nível 5",                        "dif": "Médio"},
    "conhecedor":        {"nome": "🎓 Conhecedor",        "desc": "Acertar 50 perguntas do quiz",             "dif": "Médio"},
    "em_chamas":         {"nome": "🔥 Em Chamas",         "desc": "Acertar 5 perguntas seguidas",             "dif": "Médio"},
    "top_fragger":       {"nome": "👑 Top Fragger",       "desc": "Ficar em 1° no ranking do servidor",       "dif": "Médio"},
    "duelista":          {"nome": "⚔️ Duelista",          "desc": "Vencer 10 duelos",                         "dif": "Médio"},
    "veterano":          {"nome": "🌟 Veterano",          "desc": "Chegar ao nível 15",                       "dif": "Difícil"},
    "enciclopedia":      {"nome": "🧠 Enciclopédia",      "desc": "Acertar 150 perguntas do quiz",            "dif": "Difícil"},
    "lendario":          {"nome": "💎 Lendário",          "desc": "Chegar ao nível 25",                       "dif": "Difícil"},
    "imbativel":         {"nome": "🎖️ Imbatível",         "desc": "Vencer 25 duelos seguidos",                "dif": "Muito difícil"},
    "mestre_arca":       {"nome": "🔱 Mestre da Arca",    "desc": "Conseguir todas as outras conquistas",     "dif": "Muito difícil"},
    "dedicado":          {"nome": "☀️ Dedicado",          "desc": "Usar o bot 30 dias seguidos",              "dif": "Muito difícil"},
}

def get_stats_user(uid):
    stats = carregar_stats()
    if uid not in stats:
        stats[uid] = {
            "mensagens": 0, "quiz_acertos": 0, "quiz_streak": 0,
            "duelos_venc": 0, "duelos_streak_atual": 0, "duelos_streak_max": 0,
            "dias_seguidos": 0, "ultimo_dia": "",
        }
        salvar_stats(stats)
    return stats

async def conceder(ctx, uid, chave):
    """Concede uma conquista se ainda não tiver, manda embed."""
    conq = carregar_conquistas()
    if uid not in conq:
        conq[uid] = []
    if chave in conq[uid]:
        return False
    conq[uid].append(chave)
    salvar_conquistas(conq)
    info = CONQUISTAS[chave]
    embed = discord.Embed(
        title="🏅 Nova Conquista Desbloqueada!",
        description=f"{ctx.author.mention} desbloqueou **{info['nome']}**\n*{info['desc']}*",
        color=COR_PADRAO
    )
    embed.set_footer(text=f"Dificuldade: {info['dif']} • ValBot v{VERSAO}")
    try:
        await ctx.send(embed=embed)
    except:
        pass
    return True

async def verificar_conquistas(ctx, uid):
    """Verifica e concede conquistas que o usuário desbloqueou."""
    stats = carregar_stats().get(uid, {})
    xp = carregar_xp().get(uid, {})
    times = carregar_times().get(str(ctx.guild.id), {})
    nivel = xp.get("nivel", 1)

    if stats.get("mensagens", 0) >= 1:
        await conceder(ctx, uid, "primeiro_passo")
    if stats.get("mensagens", 0) >= 100:
        await conceder(ctx, uid, "comunicador")
    if stats.get("quiz_acertos", 0) >= 10:
        await conceder(ctx, uid, "atirador_elite")
    if stats.get("quiz_acertos", 0) >= 50:
        await conceder(ctx, uid, "conhecedor")
    if stats.get("quiz_acertos", 0) >= 150:
        await conceder(ctx, uid, "enciclopedia")
    if stats.get("quiz_streak", 0) >= 5:
        await conceder(ctx, uid, "em_chamas")
    if stats.get("duelos_venc", 0) >= 10:
        await conceder(ctx, uid, "duelista")
    if stats.get("duelos_streak_max", 0) >= 25:
        await conceder(ctx, uid, "imbativel")
    if stats.get("dias_seguidos", 0) >= 30:
        await conceder(ctx, uid, "dedicado")
    if nivel >= 5:
        await conceder(ctx, uid, "escalando")
    if nivel >= 15:
        await conceder(ctx, uid, "veterano")
    if nivel >= 25:
        await conceder(ctx, uid, "lendario")

    # bem_vindo_time
    for nome_t, info_t in times.items():
        if uid in info_t.get("membros", []):
            await conceder(ctx, uid, "bem_vindo_time")
            break

    # top_fragger
    dados = carregar_xp()
    if dados:
        ranking = sorted(dados.items(), key=lambda x: x[1].get("xp", 0), reverse=True)
        if ranking and ranking[0][0] == uid:
            await conceder(ctx, uid, "top_fragger")

    # mestre_arca – todas exceto ela mesma
    conq = carregar_conquistas().get(uid, [])
    outras = [c for c in CONQUISTAS if c != "mestre_arca"]
    if all(c in conq for c in outras):
        await conceder(ctx, uid, "mestre_arca")

# ============================================================
# XP – mensagens e on_message
# ============================================================
@bot.event
async def on_message(message):
    if message.author.bot or message.guild is None:
        return

    # Servidores não autorizados: processa comandos (para o @bot.check rejeitar
    # com a mensagem correta) mas não acumula XP nem stats
    if not servidor_autorizado(message.guild.id):
        await bot.process_commands(message)
        return

    uid = str(message.author.id)
    dados = carregar_xp()
    if uid not in dados:
        dados[uid] = {"xp": 0, "nivel": 1}
    dados[uid]["xp"] += 10

    xp_atual = dados[uid]["xp"]
    nivel_novo = (xp_atual // 100) + 1
    subiu = nivel_novo > dados[uid]["nivel"]
    dados[uid]["nivel"] = nivel_novo
    salvar_xp(dados)

    # Stats: mensagens + dias seguidos
    stats = get_stats_user(uid)
    stats[uid]["mensagens"] += 1
    hoje = datetime.utcnow().strftime("%Y-%m-%d")
    ontem = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
    ult = stats[uid].get("ultimo_dia", "")
    if ult == hoje:
        pass
    elif ult == ontem:
        stats[uid]["dias_seguidos"] += 1
        stats[uid]["ultimo_dia"] = hoje
    else:
        stats[uid]["dias_seguidos"] = 1
        stats[uid]["ultimo_dia"] = hoje
    salvar_stats(stats)

    if subiu:
        await message.channel.send(
            f"🎉 Parabéns {message.author.name}! Você subiu para o nível **{nivel_novo}**!"
        )

    # Cria um ctx leve só para conceder conquistas
    class FakeCtx:
        def __init__(self, m):
            self.guild = m.guild
            self.author = m.author
            self.channel = m.channel
        async def send(self, *a, **k):
            return await self.channel.send(*a, **k)
    try:
        await verificar_conquistas(FakeCtx(message), uid)
    except:
        pass

    await bot.process_commands(message)

# ============================================================
# QUIZ – 150 perguntas + !stopquiz
# ============================================================
perguntas_usadas = {}
quiz_ativo = {}  # guild_id -> True/False

@bot.command()
@requer_acesso()
async def quiz(ctx):
    gid = str(ctx.guild.id)
    if quiz_ativo.get(gid):
        await ctx.send("⚠️ Já tem um quiz rolando! Use `!stopquiz` pra cancelar.")
        return
    quiz_ativo[gid] = True

    if gid not in perguntas_usadas:
        perguntas_usadas[gid] = []
    disponiveis = [p for p in perguntas_todas if p not in perguntas_usadas[gid]]
    if not disponiveis:
        perguntas_usadas[gid] = []
        disponiveis = perguntas_todas.copy()
        await ctx.send("🔄 Todas as 150 perguntas foram usadas! Reiniciando o banco...")

    escolha = random.choice(disponiveis)
    perguntas_usadas[gid].append(escolha)

    embed = discord.Embed(
        title="🎯 Quiz Valorant!",
        description=f"**{escolha['pergunta']}**",
        color=COR_PADRAO
    )
    embed.set_footer(text=f"⏱️ 30s pra responder • {len(disponiveis)-1} perguntas restantes")
    await ctx.send(embed=embed)

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    uid = str(ctx.author.id)
    try:
        resposta = await bot.wait_for("message", check=check, timeout=30)

        if not quiz_ativo.get(gid):  # foi cancelado
            return

        if resposta.content.lower().strip() == escolha["resposta"].lower():
            embed_ok = discord.Embed(
                title="✅ Correto!",
                description=f"Parabéns {ctx.author.name}! **+15 XP**",
                color=0x00FF88
            )
            dados = carregar_xp()
            if uid in dados:
                dados[uid]["xp"] += 15
                salvar_xp(dados)
            stats = get_stats_user(uid)
            stats[uid]["quiz_acertos"] += 1
            stats[uid]["quiz_streak"] = stats[uid].get("quiz_streak", 0) + 1
            salvar_stats(stats)
            await ctx.send(embed=embed_ok)
            await verificar_conquistas(ctx, uid)
        else:
            embed_err = discord.Embed(
                title="❌ Errado!",
                description=f"A resposta era: **{escolha['resposta']}**",
                color=COR_PADRAO
            )
            stats = get_stats_user(uid)
            stats[uid]["quiz_streak"] = 0
            salvar_stats(stats)
            await ctx.send(embed=embed_err)
    except asyncio.TimeoutError:
        await ctx.send("⏰ Tempo esgotado!")
    except:
        pass
    finally:
        quiz_ativo[gid] = False

@bot.command()
@requer_acesso()
async def stopquiz(ctx):
    gid = str(ctx.guild.id)
    if quiz_ativo.get(gid):
        quiz_ativo[gid] = False
        await ctx.send("🛑 Quiz cancelado!")
    else:
        await ctx.send("⚠️ Não tem quiz ativo no momento.")

# ============================================================
# RANK e TOP
# ============================================================
@bot.command()
@requer_acesso()
async def rank(ctx):
    dados = carregar_xp()
    uid = str(ctx.author.id)
    if uid not in dados:
        await ctx.send("Você ainda não tem XP! Manda uma mensagem pra começar.")
        return

    xp = dados[uid]["xp"]
    nivel = dados[uid]["nivel"]
    proximo = nivel * 100
    progresso = barra_progresso(xp % 100, 100, 15)

    embed = discord.Embed(
        title=f"📊 Ranking de {ctx.author.name}",
        color=COR_PADRAO
    )
    embed.add_field(name="🎖️ Nível", value=f"**{nivel}**", inline=True)
    embed.add_field(name="⭐ XP", value=f"**{xp}/{proximo}**", inline=True)
    embed.add_field(name="📈 Progresso", value=f"`{progresso}` {xp % 100}%", inline=False)
    if ctx.author.avatar:
        embed.set_thumbnail(url=ctx.author.avatar.url)
    embed.set_footer(text=f"ValBot v{VERSAO} • Sistema de Ranking")
    await ctx.send(embed=embed)

@bot.command()
@requer_acesso()
async def top(ctx):
    dados = carregar_xp()
    if not dados:
        await ctx.send("Ninguém tem XP ainda!")
        return
    ranking = sorted(dados.items(), key=lambda x: x[1].get("xp", 0), reverse=True)[:5]
    embed = discord.Embed(title="🏆 Top 5 do Servidor", color=COR_PADRAO)
    medalhas = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
    for i, (user_id, info) in enumerate(ranking):
        try:
            usuario = await bot.fetch_user(int(user_id))
            nome = usuario.name
        except:
            nome = f"User {user_id}"
        embed.add_field(
            name=f"{medalhas[i]} {nome}",
            value=f"Nível **{info.get('nivel', 1)}** • {info.get('xp', 0)} XP",
            inline=False
        )
    embed.set_footer(text=f"ValBot v{VERSAO} • Sistema de Ranking")
    await ctx.send(embed=embed)

# ============================================================
# SORTEIO
# ============================================================
@bot.command()
@requer_acesso()
async def sorteio(ctx, tempo: int = None, *, premio: str = None):
    if tempo is None or premio is None:
        await ctx.send("❌ Use: `!sorteio [segundos] [prêmio]` — ex: `!sorteio 60 Nitro`")
        return
    if tempo < 5:
        await ctx.send("⚠️ Tempo mínimo é 5 segundos.")
        return
    if tempo > 3600:
        await ctx.send("⚠️ Tempo máximo é 3600 segundos (1 hora).")
        return
    embed = discord.Embed(
        title="🎁 SORTEIO!",
        description=f"**Prêmio:** {premio}\n\nReaja com 🎉 para participar!\nTempo: **{tempo} segundos**",
        color=COR_PADRAO
    )
    embed.set_footer(text=f"Sorteio criado por {ctx.author.name}")
    mensagem = await ctx.send(embed=embed)
    await mensagem.add_reaction("🎉")
    await asyncio.sleep(tempo)
    mensagem = await ctx.channel.fetch_message(mensagem.id)
    usuarios = []
    for reacao in mensagem.reactions:
        if str(reacao.emoji) == "🎉":
            async for usuario in reacao.users():
                if not usuario.bot:
                    usuarios.append(usuario)
    if not usuarios:
        await ctx.send("❌ Ninguém participou do sorteio!")
        return
    vencedor = random.choice(usuarios)
    embed_resultado = discord.Embed(
        title="🏆 Resultado do Sorteio!",
        description=f"Parabéns {vencedor.mention}!\nVocê ganhou **{premio}**! 🎉",
        color=COR_PADRAO
    )
    await ctx.send(embed=embed_resultado)

@sorteio.error
async def sorteio_error(ctx, error):
    if isinstance(error, (commands.BadArgument, commands.MissingRequiredArgument)):
        await ctx.send("❌ Use: `!sorteio [segundos] [prêmio]` — ex: `!sorteio 60 Nitro`")

# ============================================================
# HENRIK API – !stats e !historico
# ============================================================
async def henrik_get(session, url):
    headers = {"Authorization": HENRIK_KEY}
    async with session.get(url, headers=headers) as resp:
        try:
            data = await resp.json(content_type=None)
        except Exception as e:
            print(f"[HENRIK] Falha ao parsear JSON ({url}): {e}")
            data = {}
        return resp.status, data

@bot.command()
@requer_acesso()
async def stats(ctx, *, nome: str):
    if "#" not in nome:
        await ctx.send("❌ Use o formato correto: `!stats Nome#TAG`")
        return
    player_name, player_tag = nome.split("#", 1)
    msg = await ctx.send("🔍 Buscando stats...")
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://api.henrikdev.xyz/valorant/v2/account/{player_name}/{player_tag}"
            status, perfil = await henrik_get(session, url)

            if status != 200:
                await msg.edit(content=f"❌ Erro {status}: `{perfil.get('errors', perfil.get('message', 'sem detalhe'))}`")
                return
            regiao = perfil["data"]["region"]
            _, rank_data = await henrik_get(session, f"https://api.henrikdev.xyz/valorant/v3/mmr/{regiao}/pc/{player_name}/{player_tag}")

        dados = perfil["data"]
        rank_info = rank_data.get("data", {})
        nivel = dados.get("account_level", "?")
        rank_atual = rank_info.get("current", {}).get("tier", {}).get("name", "Sem rank")
        elo = rank_info.get("current", {}).get("elo", 0)
        rr = rank_info.get("current", {}).get("rr", 0)
        progresso = barra_progresso(rr, 100, 15)
        cor = cor_por_rank(rank_atual)

        embed = discord.Embed(title=f"🎮 {player_name}#{player_tag}", color=cor)
        embed.add_field(name="🏆 Rank Atual", value=f"**{rank_atual}**", inline=True)
        embed.add_field(name="⭐ ELO", value=f"**{elo}**", inline=True)
        embed.add_field(name="🎯 RR", value=f"**{rr}/100**", inline=True)
        embed.add_field(name="📈 Progresso do RR", value=f"`{progresso}` {rr}%", inline=False)
        embed.add_field(name="🎮 Nível da Conta", value=f"**{nivel}**", inline=True)
        embed.add_field(name="🌎 Região", value=f"**{regiao.upper()}**", inline=True)
        embed.set_footer(text=f"ValBot v{VERSAO} • Powered by Henrik API")
        await msg.delete()
        await ctx.send(embed=embed)
    except Exception as e:
        print(f"[ERRO !stats] {type(e).__name__}: {e}")
        await msg.edit(content=f"❌ Erro ao buscar stats. Tente novamente.")

@bot.command()
@requer_acesso()
async def historico(ctx, *, nome: str):
    if "#" not in nome:
        await ctx.send("❌ Use o formato correto: `!historico Nome#TAG`")
        return
    player_name, player_tag = nome.split("#", 1)
    msg = await ctx.send("🔍 Buscando histórico...")
    try:
        async with aiohttp.ClientSession() as session:
            status, perfil = await henrik_get(session, f"https://api.henrikdev.xyz/valorant/v2/account/{player_name}/{player_tag}")
            if status != 200:
                await msg.edit(content="❌ Jogador não encontrado!")
                return
            regiao = perfil["data"]["region"]
            _, matches_data = await henrik_get(session, f"https://api.henrikdev.xyz/valorant/v4/matches/{regiao}/pc/{player_name}/{player_tag}?mode=competitive&size=5")

        partidas = matches_data.get("data", [])
        if not partidas:
            await msg.edit(content="❌ Nenhuma partida encontrada!")
            return

        embed = discord.Embed(
            title=f"📜 Histórico de {player_name}#{player_tag}",
            description="Últimas 5 partidas competitivas",
            color=COR_PADRAO
        )
        for partida in partidas:
            jogador = None
            for p in partida["players"]:
                if p["name"].lower() == player_name.lower() and p["tag"].lower() == player_tag.lower():
                    jogador = p
                    break
            if not jogador:
                continue
            mapa = partida["metadata"]["map"]["name"]
            resultado_time = jogador["team_id"]
            ganhou = any(t["team_id"] == resultado_time and t["won"] for t in partida.get("teams", []))
            resultado = "✅ Vitória" if ganhou else "❌ Derrota"
            stats_j = jogador.get("stats", {})
            kills = stats_j.get("kills", 0)
            deaths = stats_j.get("deaths", 1)
            assists = stats_j.get("assists", 0)
            kda = round(kills / max(deaths, 1), 2)
            agente = jogador.get("agent", {}).get("name", "?")
            embed.add_field(
                name=f"{resultado} — {mapa}",
                value=f"Agente: **{agente}** • K/D/A: **{kills}/{deaths}/{assists}** • KDA: **{kda}**",
                inline=False
            )
        embed.set_footer(text=f"ValBot v{VERSAO} • Powered by Henrik API")
        await msg.delete()
        await ctx.send(embed=embed)
    except Exception as e:
        print(f"[ERRO !historico] {type(e).__name__}: {e}")
        await msg.edit(content="❌ Erro ao buscar histórico. Tente novamente.")

# ============================================================
# PERFIL EXPANDIDO + PERSONALIZAÇÃO
# ============================================================
@bot.command()
@requer_acesso()
async def perfil(ctx, *, nome: str = None):
    if not nome or "#" not in nome:
        await ctx.send("❌ Use: `!perfil Nome#TAG`")
        return
    player_name, player_tag = nome.split("#", 1)
    msg = await ctx.send("🔍 Carregando perfil...")
    try:
        async with aiohttp.ClientSession() as session:
            status, perfil_data = await henrik_get(session, f"https://api.henrikdev.xyz/valorant/v2/account/{player_name}/{player_tag}")
            if status != 200:
                await msg.edit(content="❌ Jogador não encontrado!")
                return
            regiao = perfil_data["data"]["region"]
            _, rank_data = await henrik_get(session, f"https://api.henrikdev.xyz/valorant/v3/mmr/{regiao}/pc/{player_name}/{player_tag}")
            _, matches_data = await henrik_get(session, f"https://api.henrikdev.xyz/valorant/v4/matches/{regiao}/pc/{player_name}/{player_tag}?mode=competitive&size=10")

        rank_info = rank_data.get("data", {})
        rank_atual = rank_info.get("current", {}).get("tier", {}).get("name", "Sem rank")
        elo = rank_info.get("current", {}).get("elo", 0)
        rr = rank_info.get("current", {}).get("rr", 0)

        # Cálculo de winrate, KDA, agente/mapa favoritos
        partidas = matches_data.get("data", [])
        vit = 0
        tot_k = tot_d = tot_a = 0
        agentes_cnt, mapas_cnt = {}, {}
        for partida in partidas:
            jogador = None
            for p in partida["players"]:
                if p["name"].lower() == player_name.lower() and p["tag"].lower() == player_tag.lower():
                    jogador = p
                    break
            if not jogador:
                continue
            resultado_time = jogador["team_id"]
            if any(t["team_id"] == resultado_time and t["won"] for t in partida.get("teams", [])):
                vit += 1
            sj = jogador.get("stats", {})
            tot_k += sj.get("kills", 0)
            tot_d += sj.get("deaths", 0)
            tot_a += sj.get("assists", 0)
            ag = jogador.get("agent", {}).get("name", "?")
            mp = partida["metadata"]["map"]["name"]
            agentes_cnt[ag] = agentes_cnt.get(ag, 0) + 1
            mapas_cnt[mp] = mapas_cnt.get(mp, 0) + 1

        n_part = max(len(partidas), 1)
        winrate = round((vit / n_part) * 100, 1)
        kda = round((tot_k + tot_a) / max(tot_d, 1), 2)
        ag_top = max(agentes_cnt.items(), key=lambda x: x[1])[0] if agentes_cnt else "—"
        mp_top = max(mapas_cnt.items(), key=lambda x: x[1])[0] if mapas_cnt else "—"

        # Personalização salva
        perfis = carregar_perfis()
        uid = str(ctx.author.id)
        custom = perfis.get(uid, {})
        ag_fav = custom.get("agente", ag_top)
        arma_fav = custom.get("arma", "—")
        titulo = custom.get("titulo", "Jogador da Arca")

        # Salva o agente favorito do !meta server-wide
        perfis.setdefault("_meta", {}).setdefault(str(ctx.guild.id), {})
        perfis["_meta"][str(ctx.guild.id)][uid] = ag_top
        salvar_perfis(perfis)

        cor = cor_por_rank(rank_atual)
        embed = discord.Embed(
            title=f"🎮 {player_name}#{player_tag}",
            description=f"*{titulo}*",
            color=cor
        )
        embed.add_field(name="🏆 Rank", value=f"**{rank_atual}**", inline=True)
        embed.add_field(name="⭐ ELO", value=f"**{elo}**", inline=True)
        embed.add_field(name="🎯 RR", value=f"**{rr}/100**", inline=True)
        embed.add_field(name="📊 Winrate (10p)", value=f"**{winrate}%**", inline=True)
        embed.add_field(name="🔫 KDA Médio", value=f"**{kda}**", inline=True)
        embed.add_field(name="🌎 Região", value=f"**{regiao.upper()}**", inline=True)
        embed.add_field(name="👤 Agente Favorito", value=f"**{ag_fav.title()}**", inline=True)
        embed.add_field(name="🗺️ Mapa Mais Jogado", value=f"**{mp_top}**", inline=True)
        embed.add_field(name="🔪 Arma Favorita", value=f"**{arma_fav.title()}**", inline=True)

        img = get_agent_image(ag_fav)
        if img:
            embed.set_thumbnail(url=img)
        embed.set_footer(text=f"ValBot v{VERSAO} • Personalize com !setagente, !setarma, !settitulo")
        await msg.delete()
        await ctx.send(embed=embed)
    except Exception as e:
        print(f"[ERRO !perfil] {type(e).__name__}: {e}")
        await msg.edit(content=f"❌ Erro ao montar perfil. Tente novamente.")

@bot.command()
@requer_acesso()
async def setagente(ctx, *, nome: str):
    perfis = carregar_perfis()
    uid = str(ctx.author.id)
    perfis.setdefault(uid, {})["agente"] = nome.strip()
    salvar_perfis(perfis)
    embed = discord.Embed(
        title="✅ Agente favorito definido",
        description=f"Agente: **{nome.title()}**",
        color=COR_PADRAO
    )
    img = get_agent_image(nome)
    if img:
        embed.set_thumbnail(url=img)
    await ctx.send(embed=embed)

@bot.command()
@requer_acesso()
async def setarma(ctx, *, nome: str):
    perfis = carregar_perfis()
    uid = str(ctx.author.id)
    perfis.setdefault(uid, {})["arma"] = nome.strip()
    salvar_perfis(perfis)
    embed = discord.Embed(
        title="✅ Arma/Skin favorita definida",
        description=f"Arma: **{nome.title()}**",
        color=COR_PADRAO
    )
    await ctx.send(embed=embed)

@bot.command()
@requer_acesso()
async def settitulo(ctx, *, texto: str):
    if len(texto) > 60:
        await ctx.send("⚠️ Título muito longo (máx 60 caracteres).")
        return
    perfis = carregar_perfis()
    uid = str(ctx.author.id)
    perfis.setdefault(uid, {})["titulo"] = texto.strip()
    salvar_perfis(perfis)
    embed = discord.Embed(
        title="✅ Título personalizado definido",
        description=f"*{texto}*",
        color=COR_PADRAO
    )
    await ctx.send(embed=embed)

# ============================================================
# SISTEMA DE TIMES
# ============================================================
@bot.command()
@requer_acesso()
async def criartime(ctx, *, nome: str):
    times = carregar_times()
    gid = str(ctx.guild.id)
    times.setdefault(gid, {})
    nome_l = nome.lower()
    if nome_l in times[gid]:
        await ctx.send("⚠️ Já existe um time com esse nome!")
        return
    uid = str(ctx.author.id)
    # Sair de qualquer time anterior
    for n, info in times[gid].items():
        if uid in info.get("membros", []):
            info["membros"].remove(uid)
    times[gid][nome_l] = {"nome_display": nome, "lider": uid, "membros": [uid]}
    salvar_times(times)
    embed = discord.Embed(
        title="✅ Time criado!",
        description=f"Time **{nome}** criado por {ctx.author.mention}.\nUsa `!entrartime {nome}` pra entrar.",
        color=COR_PADRAO
    )
    await ctx.send(embed=embed)
    await verificar_conquistas(ctx, uid)

@bot.command()
@requer_acesso()
async def entrartime(ctx, *, nome: str):
    times = carregar_times()
    gid = str(ctx.guild.id)
    times.setdefault(gid, {})
    nome_l = nome.lower()
    if nome_l not in times[gid]:
        await ctx.send("❌ Time não encontrado. Veja `!timelist`.")
        return
    uid = str(ctx.author.id)
    for n, info in times[gid].items():
        if uid in info.get("membros", []):
            info["membros"].remove(uid)
    times[gid][nome_l]["membros"].append(uid)
    salvar_times(times)
    await ctx.send(f"🤝 {ctx.author.mention} entrou no time **{times[gid][nome_l]['nome_display']}**!")
    await verificar_conquistas(ctx, uid)

@bot.command()
@requer_acesso()
async def sairtime(ctx):
    times = carregar_times()
    gid = str(ctx.guild.id)
    times.setdefault(gid, {})
    uid = str(ctx.author.id)
    saiu_de = None
    for n, info in list(times[gid].items()):
        if uid in info.get("membros", []):
            info["membros"].remove(uid)
            saiu_de = info["nome_display"]
            # Se time ficou vazio remove
            if not info["membros"]:
                del times[gid][n]
            break
    salvar_times(times)
    if saiu_de:
        await ctx.send(f"👋 {ctx.author.mention} saiu do time **{saiu_de}**.")
    else:
        await ctx.send("⚠️ Você não está em nenhum time.")

@bot.command()
@requer_acesso()
async def timelist(ctx):
    times = carregar_times()
    gid = str(ctx.guild.id)
    lst = times.get(gid, {})
    if not lst:
        await ctx.send("⚠️ Nenhum time criado ainda. Use `!criartime [nome]`.")
        return
    dados_xp = carregar_xp()
    ranking = []
    for n, info in lst.items():
        xp_total = sum(dados_xp.get(m, {}).get("xp", 0) for m in info.get("membros", []))
        ranking.append((info["nome_display"], len(info["membros"]), xp_total))
    ranking.sort(key=lambda x: x[2], reverse=True)
    embed = discord.Embed(title="🛡️ Times do Servidor", color=COR_PADRAO)
    medalhas = ["🥇", "🥈", "🥉"] + ["▫️"] * 20
    for i, (n, qtd, xp) in enumerate(ranking):
        embed.add_field(
            name=f"{medalhas[i]} {n}",
            value=f"👥 {qtd} membros • ⭐ {xp} XP total",
            inline=False
        )
    embed.set_footer(text=f"ValBot v{VERSAO} • Ranking de Times")
    await ctx.send(embed=embed)

@bot.command()
@requer_acesso()
async def timeinfo(ctx, *, nome: str):
    times = carregar_times()
    gid = str(ctx.guild.id)
    nome_l = nome.lower()
    if nome_l not in times.get(gid, {}):
        await ctx.send("❌ Time não encontrado.")
        return
    info = times[gid][nome_l]
    dados_xp = carregar_xp()
    membros_str = ""
    xp_total = 0
    for m in info["membros"]:
        try:
            u = await bot.fetch_user(int(m))
            n = u.name
        except:
            n = f"User {m}"
        xp_m = dados_xp.get(m, {}).get("xp", 0)
        xp_total += xp_m
        lider = " 👑" if m == info["lider"] else ""
        membros_str += f"• {n}{lider} — {xp_m} XP\n"

    embed = discord.Embed(title=f"🛡️ {info['nome_display']}", color=COR_PADRAO)
    embed.add_field(name="👥 Membros", value=membros_str or "—", inline=False)
    embed.add_field(name="⭐ XP Total", value=f"**{xp_total}**", inline=True)
    embed.add_field(name="📦 Tamanho", value=f"**{len(info['membros'])}**", inline=True)
    embed.set_footer(text=f"ValBot v{VERSAO} • Time Info")
    await ctx.send(embed=embed)

# ============================================================
# NOVOS COMANDOS: !duelo, !missão, !meta, !ajuda
# ============================================================
duelos_ativos = {}  # (gid, uid) -> True

@bot.command()
@requer_acesso()
async def duelo(ctx, oponente: discord.Member):
    if oponente.bot or oponente.id == ctx.author.id:
        await ctx.send("⚠️ Escolha outro jogador (não bot e não você mesmo).")
        return
    gid = str(ctx.guild.id)
    key1 = (gid, ctx.author.id)
    key2 = (gid, oponente.id)
    if duelos_ativos.get(key1) or duelos_ativos.get(key2):
        await ctx.send("⚠️ Um dos jogadores já está em duelo.")
        return
    duelos_ativos[key1] = True
    duelos_ativos[key2] = True

    embed = discord.Embed(
        title="⚔️ DUELO DE QUIZ!",
        description=f"{ctx.author.mention} desafiou {oponente.mention} para um duelo de 5 perguntas!\n\n"
                    f"{oponente.mention}, digite `aceitar` em 30s para aceitar.",
        color=COR_PADRAO
    )
    await ctx.send(embed=embed)

    def check_aceite(m):
        return m.author.id == oponente.id and m.channel == ctx.channel and m.content.lower() == "aceitar"
    try:
        await bot.wait_for("message", check=check_aceite, timeout=30)
    except asyncio.TimeoutError:
        await ctx.send("⏰ O oponente não aceitou o duelo.")
        duelos_ativos.pop(key1, None)
        duelos_ativos.pop(key2, None)
        return

    pontos = {ctx.author.id: 0, oponente.id: 0}
    perguntas_d = random.sample(perguntas_todas, 5)

    for i, q in enumerate(perguntas_d, 1):
        emb_q = discord.Embed(
            title=f"⚔️ Pergunta {i}/5",
            description=f"**{q['pergunta']}**\n\nPrimeiro a responder certo ganha o ponto! (20s)",
            color=COR_PADRAO
        )
        await ctx.send(embed=emb_q)
        def check_q(m):
            return m.author.id in (ctx.author.id, oponente.id) and m.channel == ctx.channel
        try:
            tempo_fim = asyncio.get_running_loop().time() + 20
            vencedor_rodada = None
            while True:
                restante = tempo_fim - asyncio.get_running_loop().time()
                if restante <= 0:
                    break
                resp = await bot.wait_for("message", check=check_q, timeout=restante)
                if resp.content.lower().strip() == q["resposta"].lower():
                    pontos[resp.author.id] += 1
                    vencedor_rodada = resp.author
                    await ctx.send(f"✅ {resp.author.mention} acertou! +1 ponto")
                    break
            if not vencedor_rodada:
                await ctx.send(f"⏰ Ninguém acertou. A resposta era: **{q['resposta']}**")
        except asyncio.TimeoutError:
            await ctx.send(f"⏰ Tempo! A resposta era: **{q['resposta']}**")

    duelos_ativos.pop(key1, None)
    duelos_ativos.pop(key2, None)

    p1, p2 = pontos[ctx.author.id], pontos[oponente.id]
    if p1 > p2:
        venc, perd = ctx.author, oponente
    elif p2 > p1:
        venc, perd = oponente, ctx.author
    else:
        venc = perd = None

    desc = f"🏆 **{ctx.author.name}**: {p1} pts\n🏆 **{oponente.name}**: {p2} pts\n\n"
    if venc:
        desc += f"Vencedor: {venc.mention} 🎉"
        uid_v = str(venc.id)
        uid_p = str(perd.id)
        stats = get_stats_user(uid_v)
        get_stats_user(uid_p)  # garante criação
        stats = carregar_stats()
        stats[uid_v]["duelos_venc"] = stats[uid_v].get("duelos_venc", 0) + 1
        stats[uid_v]["duelos_streak_atual"] = stats[uid_v].get("duelos_streak_atual", 0) + 1
        if stats[uid_v]["duelos_streak_atual"] > stats[uid_v].get("duelos_streak_max", 0):
            stats[uid_v]["duelos_streak_max"] = stats[uid_v]["duelos_streak_atual"]
        stats[uid_p]["duelos_streak_atual"] = 0
        salvar_stats(stats)
        await verificar_conquistas(ctx, uid_v)
    else:
        desc += "Empate! Nenhum vencedor."

    emb_fim = discord.Embed(title="⚔️ Resultado do Duelo", description=desc, color=COR_PADRAO)
    await ctx.send(embed=emb_fim)

MISSOES = [
    {"desc": "Mande 20 mensagens hoje",            "xp": 30, "tipo": "msg",  "alvo": 20},
    {"desc": "Acerte 3 perguntas no !quiz",        "xp": 50, "tipo": "quiz", "alvo": 3},
    {"desc": "Vença 1 duelo hoje",                 "xp": 40, "tipo": "duelo","alvo": 1},
    {"desc": "Use o bot 1 vez (já feito!)",        "xp": 20, "tipo": "msg",  "alvo": 1},
    {"desc": "Mande 50 mensagens hoje",            "xp": 70, "tipo": "msg",  "alvo": 50},
]

@bot.command()
@requer_acesso()
async def missao(ctx):
    uid = str(ctx.author.id)
    # Missão diária baseada no dia + uid (assim cada user tem missão fixa do dia)
    hoje = datetime.utcnow().strftime("%Y%m%d")
    seed = int(hoje) + sum(ord(c) for c in uid)
    random.seed(seed)
    m = random.choice(MISSOES)
    random.seed()  # reset

    stats = carregar_stats().get(uid, {})
    if m["tipo"] == "msg":
        atual = stats.get("mensagens", 0)
    elif m["tipo"] == "quiz":
        atual = stats.get("quiz_acertos", 0)
    else:
        atual = stats.get("duelos_venc", 0)

    progresso = barra_progresso(min(atual, m["alvo"]), m["alvo"], 15)
    completa = atual >= m["alvo"]
    status = "✅ Completa!" if completa else "🔄 Em andamento"

    embed = discord.Embed(
        title="🎯 Missão Diária",
        description=f"**{m['desc']}**\n\nRecompensa: **+{m['xp']} XP**",
        color=COR_PADRAO
    )
    embed.add_field(name="Progresso", value=f"`{progresso}` {min(atual, m['alvo'])}/{m['alvo']}", inline=False)
    embed.add_field(name="Status", value=status, inline=False)

    # Dá XP de recompensa se completa e ainda não pegou hoje
    perfis = carregar_perfis()
    chave = f"missao_{hoje}"
    if completa and perfis.get(uid, {}).get(chave) != True:
        perfis.setdefault(uid, {})[chave] = True
        salvar_perfis(perfis)
        dados = carregar_xp()
        if uid not in dados:
            dados[uid] = {"xp": 0, "nivel": 1}
        dados[uid]["xp"] += m["xp"]
        salvar_xp(dados)
        embed.set_footer(text=f"+{m['xp']} XP recebido! • ValBot v{VERSAO}")
    else:
        embed.set_footer(text=f"ValBot v{VERSAO} • Missão diária")
    await ctx.send(embed=embed)

@bot.command()
@requer_acesso()
async def meta(ctx):
    perfis = carregar_perfis()
    gid = str(ctx.guild.id)
    agentes_srv = perfis.get("_meta", {}).get(gid, {})
    if not agentes_srv:
        await ctx.send("⚠️ Ainda ninguém usou `!perfil` neste servidor.")
        return
    cnt = {}
    for uid, ag in agentes_srv.items():
        cnt[ag] = cnt.get(ag, 0) + 1
    top5 = sorted(cnt.items(), key=lambda x: x[1], reverse=True)[:5]
    embed = discord.Embed(
        title="📊 Meta do Servidor – Top 5 Agentes",
        description="Agentes mais usados pelos jogadores do servidor (via !perfil)",
        color=COR_PADRAO
    )
    medalhas = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
    for i, (ag, q) in enumerate(top5):
        embed.add_field(name=f"{medalhas[i]} {ag.title()}", value=f"**{q}** jogadores", inline=False)
    img = get_agent_image(top5[0][0]) if top5 else None
    if img:
        embed.set_thumbnail(url=img)
    embed.set_footer(text=f"ValBot v{VERSAO} • Meta do Servidor")
    await ctx.send(embed=embed)

@bot.command()
async def ajuda(ctx):
    embed = discord.Embed(
        title="📚 Guia do ValBot",
        description=f"Comandos disponíveis (v{VERSAO})",
        color=COR_PADRAO
    )
    embed.add_field(
        name="🎮 Diversão",
        value=(
            "`!quiz` – Pergunta de Valorant (+15 XP)\n"
            "`!stopquiz` – Cancela quiz ativo\n"
            "`!duelo @user` – Quiz 1v1 (melhor de 5)\n"
            "`!sorteio [tempo] [prêmio]` – Sorteio com reação\n"
            "`!missao` – Missão diária"
        ),
        inline=False
    )
    embed.add_field(
        name="📊 Stats & Ranking",
        value=(
            "`!rank` – Seu XP e nível\n"
            "`!top` – Top 5 do servidor\n"
            "`!stats Nome#TAG` – Stats reais da Riot\n"
            "`!historico Nome#TAG` – Últimas 5 partidas\n"
            "`!perfil Nome#TAG` – Perfil completo com winrate/KDA\n"
            "`!meta` – Top 5 agentes do servidor"
        ),
        inline=False
    )
    embed.add_field(
        name="🎨 Personalização",
        value=(
            "`!setagente [nome]` – Agente favorito\n"
            "`!setarma [nome]` – Arma/skin favorita\n"
            "`!settitulo [texto]` – Título personalizado"
        ),
        inline=False
    )
    embed.add_field(
        name="🛡️ Times",
        value=(
            "`!criartime [nome]` – Cria um time\n"
            "`!entrartime [nome]` – Entra em um time\n"
            "`!sairtime` – Sai do time atual\n"
            "`!timelist` – Ranking dos times\n"
            "`!timeinfo [nome]` – Detalhes do time"
        ),
        inline=False
    )
    embed.add_field(
        name="🏅 Outros",
        value=(
            "`!conquistas` – Suas conquistas\n"
            "`!patchnotes` – Últimas atualizações\n"
            "`!ping` – Testa o bot"
        ),
        inline=False
    )
    embed.set_footer(text=f"ValBot por Arca • R$ 40/mês via LivePix • https://discord.gg/VKHG6MFh")
    await ctx.send(embed=embed)

# ============================================================
# CONQUISTAS – comando público
# ============================================================
@bot.command()
@requer_acesso()
async def conquistas(ctx):
    uid = str(ctx.author.id)
    conq = carregar_conquistas().get(uid, [])
    desc = ""
    for chave, info in CONQUISTAS.items():
        marca = "✅" if chave in conq else "🔒"
        desc += f"{marca} **{info['nome']}** — *{info['desc']}* `({info['dif']})`\n"
    embed = discord.Embed(
        title=f"🏅 Conquistas de {ctx.author.name}",
        description=desc,
        color=COR_PADRAO
    )
    embed.set_footer(text=f"{len(conq)}/{len(CONQUISTAS)} desbloqueadas • ValBot v{VERSAO}")
    await ctx.send(embed=embed)

# ============================================================
# PATCH NOTES
# ============================================================
@bot.command()
@requer_acesso()
async def patchnotes(ctx):
    notas = carregar_patch()
    if not notas:
        await ctx.send("⚠️ Nenhuma atualização registrada.")
        return
    embed = discord.Embed(
        title="📜 Patch Notes ValBot",
        description="Últimas atualizações:",
        color=COR_PADRAO
    )
    for nota in notas[:5]:
        mudancas = "\n".join(f"• {m}" for m in nota.get("mudancas", []))
        embed.add_field(
            name=f"v{nota['versao']} — {nota['data']}",
            value=mudancas[:1020] + ("..." if len(mudancas) > 1020 else ""),
            inline=False
        )
    embed.set_footer(text=f"ValBot v{VERSAO} • Arca")
    await ctx.send(embed=embed)

# ============================================================
# RUN
# ============================================================
bot.run(TOKEN)
