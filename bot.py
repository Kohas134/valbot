import discord
import os
import json
import random
import asyncio
import aiohttp
import traceback
from datetime import datetime, timedelta, timezone
from discord.ext import commands, tasks
from dotenv import load_dotenv
from auth import (servidor_autorizado, status_servidor, carregar_autorizados,
                  carregar_testes, salvar_testes,
                  carregar_pagantes, salvar_pagantes)
from perguntas import perguntas_todas

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
HENRIK_KEY = os.getenv("HENRIK_KEY", "")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

SEU_ID = "1511753229480755356"
VERSAO = "2.1"

# ── Paleta de cores ───────────────────────────────────────────────────────────
COR_PADRAO  = 0xFF4655   # vermelho Valorant  (erros, neutro)
COR_SUCESSO = 0x00FF88   # verde              (acertos, sucesso)
COR_NEUTRO  = 0x7B2D8B   # roxo Arca          (info, listagens)
COR_OURO    = 0xFFD700   # dourado            (conquistas, sorteio)

# ── Cores exatas por rank ─────────────────────────────────────────────────────
CORES_RANK = {
    "Iron":      0x8D8D8D,
    "Bronze":    0xA05A2C,
    "Silver":    0xB0C4C4,
    "Gold":      0xFFD700,
    "Platinum":  0x26D4B0,
    "Diamond":   0x4FC3F7,
    "Ascendant": 0x00FF6A,
    "Immortal":  0xFF4444,
    "Radiant":   0xFFE566,
}

# ── Ícones oficiais de rank (valorant-api.com) ────────────────────────────────
RANK_ICONS = {
    "Iron":      "https://media.valorant-api.com/competitivetiers/03621f52-342b-cf4e-4f86-9350a49c6d04/3/largeicon.png",
    "Bronze":    "https://media.valorant-api.com/competitivetiers/03621f52-342b-cf4e-4f86-9350a49c6d04/6/largeicon.png",
    "Silver":    "https://media.valorant-api.com/competitivetiers/03621f52-342b-cf4e-4f86-9350a49c6d04/9/largeicon.png",
    "Gold":      "https://media.valorant-api.com/competitivetiers/03621f52-342b-cf4e-4f86-9350a49c6d04/12/largeicon.png",
    "Platinum":  "https://media.valorant-api.com/competitivetiers/03621f52-342b-cf4e-4f86-9350a49c6d04/15/largeicon.png",
    "Diamond":   "https://media.valorant-api.com/competitivetiers/03621f52-342b-cf4e-4f86-9350a49c6d04/18/largeicon.png",
    "Ascendant": "https://media.valorant-api.com/competitivetiers/03621f52-342b-cf4e-4f86-9350a49c6d04/21/largeicon.png",
    "Immortal":  "https://media.valorant-api.com/competitivetiers/03621f52-342b-cf4e-4f86-9350a49c6d04/24/largeicon.png",
    "Radiant":   "https://media.valorant-api.com/competitivetiers/03621f52-342b-cf4e-4f86-9350a49c6d04/27/largeicon.png",
}

# ── Curiosidades para o quiz (resposta → dica) ────────────────────────────────
CURIOSIDADES = {
    "jett":       "💡 Jett é sul-coreana e foi a agente mais popular do lançamento.",
    "vandal":     "💡 A Vandal é inspirada na AK-47 e mata com 1 headshot a qualquer distância.",
    "phantom":    "💡 O Phantom tem silenciador — não aparece no minimapa inimigo ao atirar.",
    "operator":   "💡 A Operator é a arma mais cara do jogo: 4700 créditos.",
    "sage":       "💡 Sage foi a única agente capaz de ressuscitar aliados desde o beta.",
    "sova":       "💡 O Recon Bolt do Sova pode revelar inimigos através de paredes.",
    "omen":       "💡 Ninguém sabe a verdadeira identidade do Omen — nem ele mesmo.",
    "reyna":      "💡 Reyna é totalmente auto-suficiente — não tem habilidades de suporte.",
    "raze":       "💡 Raze é brasileira de Salvador, BA, e usa tecnologia de foguetes caseiros.",
    "killjoy":    "💡 Killjoy tem o maior arsenal de gadgets defensivos do jogo.",
    "cypher":     "💡 Cypher pode usar a Neural Theft em inimigos mortos para revelar todos os outros.",
    "brimstone":  "💡 Brimstone é o líder do Protocolo VALORANT e o primeiro agente revelado.",
    "kay/o":      "💡 KAY/O é um robô do futuro que veio matar Radiants antes que destruam o mundo.",
    "neon":       "💡 Neon é a agente mais rápida do Valorant — corre mais que qualquer outro.",
    "chamber":    "💡 Chamber foi considerado OP por meses e recebeu vários nerfs seguidos.",
    "bind":       "💡 Bind foi o primeiro mapa revelado do Valorant, ainda no período de beta.",
    "haven":      "💡 Haven é o único mapa com 3 sites (A, B e C).",
    "sheriff":    "💡 O Sheriff mata com 1 headshot a qualquer distância — única pistola com esse poder.",
    "radiant":    "💡 Radiant é o rank máximo — apenas os 500 melhores jogadores por região o alcançam.",
    "loud":       "💡 A LOUD foi a primeira organização brasileira campeã mundial de Valorant (2022).",
    "aspas":      "💡 aspas foi eleito MVP do Champions 2022 com performances históricas.",
    "operator":   "💡 A Operator pode matar com 1 tiro no corpo, mesmo com escudo completo.",
    "13":         "💡 O time que chegar a 13 rounds primeiro vence — exceto em overtime (12x12).",
    "5":          "💡 Cada time tem 5 jogadores, totalizando 10 em cada partida competitiva.",
    "spike":      "💡 A Spike precisa de 4s para plantar e 7s para defusar — timing é tudo.",
    "viper":      "💡 A Pit da Viper é considerada uma das ultis mais fortes do jogo em fechamento.",
    "skye":       "💡 Skye é australiana e usa animais espirituais do folclore aborígene.",
    "saadhak":    "💡 saadhak é argentino e foi IGL da LOUD no título mundial de 2022.",
}

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

def carregar_xp():        return carregar_json("xp.json", {})
def salvar_xp(d):         salvar_json("xp.json", d)
def carregar_perfis():    return carregar_json("perfis.json", {})
def salvar_perfis(d):     salvar_json("perfis.json", d)
def carregar_times():     return carregar_json("times.json", {})
def salvar_times(d):      salvar_json("times.json", d)
def carregar_conquistas(): return carregar_json("conquistas.json", {})
def salvar_conquistas(d): salvar_json("conquistas.json", d)
def carregar_stats():     return carregar_json("stats.json", {})
def salvar_stats(d):      salvar_json("stats.json", d)
def carregar_patch():     return carregar_json("patch_notes.json", [])

# ============================================================
# HELPERS – visuais
# ============================================================
def ft(extra=""):
    """Footer padrão com timestamp."""
    ts = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M UTC")
    base = f"ValBot v{VERSAO} • Arca"
    return f"{base} • {extra} • {ts}" if extra else f"{base} • {ts}"

def sep():
    """Campo separador invisível."""
    return ("​", "​", False)

def get_agent_image(nome):
    if not nome:
        return None
    return AGENT_IMAGES.get(nome.lower())

def get_rank_icon(rank_nome):
    if not rank_nome:
        return None
    for nome, url in RANK_ICONS.items():
        if nome.lower() in rank_nome.lower():
            return url
    return None

def cor_por_rank(rank_atual):
    if not rank_atual:
        return COR_PADRAO
    for nome, cor in CORES_RANK.items():
        if nome.lower() in rank_atual.lower():
            return cor
    return COR_PADRAO

def barra_progresso(atual, total, tamanho=15):
    if total <= 0:
        return "░" * tamanho
    proporcao = max(0, min(1, atual / total))
    cheios = int(proporcao * tamanho)
    vazios = tamanho - cheios
    return "▰" * cheios + "▱" * vazios

# ── URLs de agentes ───────────────────────────────────────────────────────────
AGENT_IMAGES = {
    "jett":      "https://media.valorant-api.com/agents/add6443a-41bd-e414-f6ad-e58d267f4e95/displayicon.png",
    "phoenix":   "https://media.valorant-api.com/agents/eb93336a-449b-9c1b-0a54-a891f7921d69/displayicon.png",
    "sage":      "https://media.valorant-api.com/agents/569fdd95-4d10-43ab-ca70-79becc718b46/displayicon.png",
    "sova":      "https://media.valorant-api.com/agents/ded3520f-4264-bfed-162d-b080e2abccf9/displayicon.png",
    "viper":     "https://media.valorant-api.com/agents/707eab51-4836-f488-046a-cda6bf494859/displayicon.png",
    "cypher":    "https://media.valorant-api.com/agents/117ed9e3-49f3-6512-3ccf-0cada7e3823b/displayicon.png",
    "reyna":     "https://media.valorant-api.com/agents/a3bfb853-43b2-7238-a4f1-ad90e9e46bcc/displayicon.png",
    "killjoy":   "https://media.valorant-api.com/agents/1e58de9c-4950-5125-93e9-a0aee9f98746/displayicon.png",
    "breach":    "https://media.valorant-api.com/agents/5f8d3a7f-467b-97f3-062c-13acf203c006/displayicon.png",
    "omen":      "https://media.valorant-api.com/agents/8e253930-4c05-31dd-1b6c-968525494517/displayicon.png",
    "brimstone": "https://media.valorant-api.com/agents/9f0d8ba9-4140-b941-57d3-a7ad57c6b417/displayicon.png",
    "raze":      "https://media.valorant-api.com/agents/f94c3b30-42be-e959-889c-5aa313dba261/displayicon.png",
    "skye":      "https://media.valorant-api.com/agents/6f2a04ca-43e0-be17-7f36-b3908627744d/displayicon.png",
    "yoru":      "https://media.valorant-api.com/agents/7f94d92c-4234-0a36-9646-3a87eb8b5c89/displayicon.png",
    "astra":     "https://media.valorant-api.com/agents/41fb69c1-4189-7b37-f117-bcaf1e96f1bf/displayicon.png",
    "kay/o":     "https://media.valorant-api.com/agents/601dbbe7-43ce-be57-2a40-4abd24953621/displayicon.png",
    "chamber":   "https://media.valorant-api.com/agents/22697a3d-45bf-8dd7-4fec-84a9e28c69d7/displayicon.png",
    "neon":      "https://media.valorant-api.com/agents/bb2a4828-46eb-8cd1-e765-15848195d751/displayicon.png",
    "fade":      "https://media.valorant-api.com/agents/dade69b4-4f5a-8528-247b-219e5a1facd6/displayicon.png",
    "harbor":    "https://media.valorant-api.com/agents/95b78ed7-4637-86d9-7e41-71ba8c293152/displayicon.png",
    "gekko":     "https://media.valorant-api.com/agents/e370fa57-4757-3604-3648-499e1f642d3f/displayicon.png",
    "deadlock":  "https://media.valorant-api.com/agents/cc8b64c8-4b25-4ff9-6e7f-37b4da43d235/displayicon.png",
    "iso":       "https://media.valorant-api.com/agents/0e38b510-41a8-5780-5e8f-568b2a4f2d6c/displayicon.png",
    "clove":     "https://media.valorant-api.com/agents/1dbf2edd-7729-4540-b09c-c0a3b9aa20a4/displayicon.png",
    "vyse":      "https://media.valorant-api.com/agents/efba5359-4016-a1e5-7626-b1ae76895940/displayicon.png",
    "tejo":      "https://media.valorant-api.com/agents/b444168c-4e35-8076-db47-ef9bf368f384/displayicon.png",
    "waylay":    "https://media.valorant-api.com/agents/df1cb487-4902-002e-5c17-d28e83e78588/displayicon.png",
}

# ============================================================
# AUTORIZAÇÃO
# ============================================================
SERVIDORES_GRATUITOS_BOT = ["1511754478913720410"]

def requer_acesso():
    async def predicate(ctx):
        autorizados = carregar_autorizados()
        if str(ctx.guild.id) in SERVIDORES_GRATUITOS_BOT or str(ctx.guild.id) in autorizados:
            return True
        st = status_servidor(ctx.guild.id)
        if st == "expirado":
            await ctx.send("❌ O acesso ao ValBot deste servidor expirou. Para renovar: https://discord.gg/VKHG6MFh")
        else:
            await ctx.send("⚠️ Este servidor não tem acesso ao ValBot. Entre em contato: https://discord.gg/VKHG6MFh")
        return False
    return commands.check(predicate)

async def _avisar_guild(sid, mensagem):
    guild = bot.get_guild(int(sid))
    if not guild:
        return
    canal = next((c for c in guild.text_channels if c.permissions_for(guild.me).send_messages), None)
    if canal:
        await canal.send(mensagem)

@tasks.loop(minutes=60)
async def verificar_acessos_expirando():
    testes = carregar_testes()
    testes_alt = False
    for sid, info in testes.items():
        if info.get("aviso_enviado"):
            continue
        inicio = datetime.fromisoformat(info["inicio"])
        if inicio.tzinfo is None:
            inicio = inicio.replace(tzinfo=timezone.utc)
        if (datetime.now(timezone.utc) - inicio).total_seconds() / 3600 >= 48:
            await _avisar_guild(sid,
                "⏰ Seu período de teste do ValBot está acabando! Faltam menos de 24h. "
                "Para continuar: https://discord.gg/VKHG6MFh")
            testes[sid]["aviso_enviado"] = True
            testes_alt = True
    if testes_alt:
        salvar_testes(testes)

    pagantes = carregar_pagantes()
    pag_alt = False
    for sid, info in pagantes.items():
        if info.get("aviso_enviado"):
            continue
        exp = datetime.fromisoformat(info["expiracao"])
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        dias = (exp - datetime.now(timezone.utc)).total_seconds() / 86400
        if 0 < dias <= 7:
            await _avisar_guild(sid,
                f"⏰ Sua assinatura do ValBot expira em **{int(dias)+1} dia(s)** "
                f"({exp.strftime('%d/%m/%Y')}). Para renovar: https://discord.gg/VKHG6MFh")
            pagantes[sid]["aviso_enviado"] = True
            pag_alt = True
    if pag_alt:
        salvar_pagantes(pagantes)

# ============================================================
# LOGS + ERROS GLOBAIS
# ============================================================
LOG_FILE = "logs.txt"

def registrar_log(ctx):
    agora = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    servidor = f"{ctx.guild.name} ({ctx.guild.id})" if ctx.guild else "DM"
    usuario = f"{ctx.author} ({ctx.author.id})"
    linha = f"[{agora}] | Servidor: {servidor} | Usuário: {usuario} | Comando: {ctx.message.content[:200]}\n"
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(linha)
    except Exception as e:
        print(f"[LOG ERROR] {e}")

@bot.event
async def on_command(ctx):
    registrar_log(ctx)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        return
    if isinstance(error, (commands.MissingRequiredArgument, commands.BadArgument)):
        return
    if isinstance(error, commands.CommandNotFound):
        return
    tb = "".join(traceback.format_exception(type(error), error, error.__traceback__))
    print(f"[ERRO GLOBAL] Comando: {ctx.command} | {type(error).__name__}: {error}\n{tb}")
    try:
        await ctx.send("❌ Ocorreu um erro inesperado. O bot continua funcionando normalmente.")
    except Exception:
        pass

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name=f"!ajuda | ValBot v{VERSAO}"))
    print(f"Bot ligado! Logado como {bot.user} | v{VERSAO}")
    print(f"Henrik Key: {HENRIK_KEY[:15]}...")
    if not verificar_acessos_expirando.is_running():
        verificar_acessos_expirando.start()

@bot.command()
async def ping(ctx):
    latencia = round(bot.latency * 1000)
    embed = discord.Embed(title="🏓 Pong!", description=f"Latência: **{latencia}ms**", color=COR_SUCESSO)
    embed.set_footer(text=ft())
    await ctx.send(embed=embed)

# ============================================================
# CONQUISTAS – definição e verificação
# ============================================================
CONQUISTAS = {
    "primeiro_passo": {"nome": "🌱 Primeiro Passo",    "desc": "Mandar primeira mensagem",              "dif": "Fácil"},
    "atirador_elite": {"nome": "🎯 Atirador de Elite",  "desc": "Acertar 10 perguntas do quiz",          "dif": "Fácil"},
    "comunicador":    {"nome": "💬 Comunicador",         "desc": "Mandar 100 mensagens",                  "dif": "Fácil"},
    "bem_vindo_time": {"nome": "🤝 Bem Vindo ao Time",  "desc": "Entrar em um time",                     "dif": "Fácil"},
    "escalando":      {"nome": "🏆 Escalando",           "desc": "Chegar ao nível 5",                     "dif": "Médio"},
    "conhecedor":     {"nome": "🎓 Conhecedor",          "desc": "Acertar 50 perguntas do quiz",          "dif": "Médio"},
    "em_chamas":      {"nome": "🔥 Em Chamas",           "desc": "Acertar 5 perguntas seguidas",          "dif": "Médio"},
    "top_fragger":    {"nome": "👑 Top Fragger",         "desc": "Ficar em 1° no ranking do servidor",    "dif": "Médio"},
    "duelista":       {"nome": "⚔️ Duelista",            "desc": "Vencer 10 duelos",                      "dif": "Médio"},
    "veterano":       {"nome": "🌟 Veterano",            "desc": "Chegar ao nível 15",                    "dif": "Difícil"},
    "enciclopedia":   {"nome": "🧠 Enciclopédia",        "desc": "Acertar 150 perguntas do quiz",         "dif": "Difícil"},
    "lendario":       {"nome": "💎 Lendário",            "desc": "Chegar ao nível 25",                    "dif": "Difícil"},
    "imbativel":      {"nome": "🎖️ Imbatível",           "desc": "Vencer 25 duelos seguidos",             "dif": "Muito Difícil"},
    "mestre_arca":    {"nome": "🔱 Mestre da Arca",      "desc": "Conseguir todas as outras conquistas",  "dif": "Muito Difícil"},
    "dedicado":       {"nome": "☀️ Dedicado",            "desc": "Usar o bot 30 dias seguidos",           "dif": "Muito Difícil"},
}

# Agrupamento por dificuldade para o !conquistas
DIFS_ORDEM = ["Fácil", "Médio", "Difícil", "Muito Difícil"]
DIFS_EMOJI = {"Fácil": "🟢", "Médio": "🟡", "Difícil": "🔴", "Muito Difícil": "💀"}

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
    conq = carregar_conquistas()
    if uid not in conq:
        conq[uid] = []
    if chave in conq[uid]:
        return False
    conq[uid].append(chave)
    salvar_conquistas(conq)
    info = CONQUISTAS[chave]
    embed = discord.Embed(
        title="🏅 CONQUISTA DESBLOQUEADA!",
        description=(
            f"{ctx.author.mention} acabou de desbloquear\n"
            f"# {info['nome']}\n"
            f"*{info['desc']}*"
        ),
        color=COR_OURO
    )
    embed.set_footer(text=ft(f"Dificuldade: {info['dif']}"))
    if ctx.author.avatar:
        embed.set_thumbnail(url=ctx.author.avatar.url)
    try:
        await ctx.send(embed=embed)
    except:
        pass
    return True

async def verificar_conquistas(ctx, uid):
    stats = carregar_stats().get(uid, {})
    xp    = carregar_xp().get(uid, {})
    times = carregar_times().get(str(ctx.guild.id), {})
    nivel = xp.get("nivel", 1)

    checks = [
        (stats.get("mensagens", 0) >= 1,   "primeiro_passo"),
        (stats.get("mensagens", 0) >= 100,  "comunicador"),
        (stats.get("quiz_acertos", 0) >= 10,  "atirador_elite"),
        (stats.get("quiz_acertos", 0) >= 50,  "conhecedor"),
        (stats.get("quiz_acertos", 0) >= 150, "enciclopedia"),
        (stats.get("quiz_streak", 0) >= 5,   "em_chamas"),
        (stats.get("duelos_venc", 0) >= 10,  "duelista"),
        (stats.get("duelos_streak_max", 0) >= 25, "imbativel"),
        (stats.get("dias_seguidos", 0) >= 30, "dedicado"),
        (nivel >= 5,  "escalando"),
        (nivel >= 15, "veterano"),
        (nivel >= 25, "lendario"),
    ]
    for condicao, chave in checks:
        if condicao:
            await conceder(ctx, uid, chave)

    for _, info_t in times.items():
        if uid in info_t.get("membros", []):
            await conceder(ctx, uid, "bem_vindo_time")
            break

    dados = carregar_xp()
    if dados:
        ranking = sorted(dados.items(), key=lambda x: x[1].get("xp", 0), reverse=True)
        if ranking and ranking[0][0] == uid:
            await conceder(ctx, uid, "top_fragger")

    conq = carregar_conquistas().get(uid, [])
    if all(c in conq for c in CONQUISTAS if c != "mestre_arca"):
        await conceder(ctx, uid, "mestre_arca")

# ============================================================
# XP – on_message
# ============================================================
@bot.event
async def on_message(message):
    if message.author.bot or message.guild is None:
        return

    if not servidor_autorizado(message.guild.id):
        await bot.process_commands(message)
        return

    uid = str(message.author.id)
    dados = carregar_xp()
    if uid not in dados:
        dados[uid] = {"xp": 0, "nivel": 1}
    dados[uid]["xp"] += 10

    xp_atual  = dados[uid]["xp"]
    nivel_novo = (xp_atual // 100) + 1
    subiu     = nivel_novo > dados[uid]["nivel"]
    dados[uid]["nivel"] = nivel_novo
    salvar_xp(dados)

    stats = get_stats_user(uid)
    stats[uid]["mensagens"] += 1
    hoje  = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    ontem = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
    ult   = stats[uid].get("ultimo_dia", "")
    if ult == ontem:
        stats[uid]["dias_seguidos"] += 1
        stats[uid]["ultimo_dia"] = hoje
    elif ult != hoje:
        stats[uid]["dias_seguidos"] = 1
        stats[uid]["ultimo_dia"] = hoje
    salvar_stats(stats)

    if subiu:
        embed_nv = discord.Embed(
            title="🎉 SUBIU DE NÍVEL!",
            description=f"Parabéns {message.author.mention}! Você chegou ao nível **{nivel_novo}**! 🚀",
            color=COR_OURO
        )
        embed_nv.set_footer(text=ft())
        await message.channel.send(embed=embed_nv)

    class FakeCtx:
        def __init__(self, m):
            self.guild = m.guild; self.author = m.author; self.channel = m.channel
        async def send(self, *a, **k):
            return await self.channel.send(*a, **k)
    try:
        await verificar_conquistas(FakeCtx(message), uid)
    except:
        pass

    await bot.process_commands(message)

# ============================================================
# QUIZ
# ============================================================
perguntas_usadas = {}
quiz_ativo = {}
_quiz_contador = {}   # gid -> número da pergunta na sessão

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
        embed_reset = discord.Embed(
            description="🔄 Todas as perguntas foram usadas! Reiniciando o banco...",
            color=COR_NEUTRO
        )
        await ctx.send(embed=embed_reset)

    _quiz_contador[gid] = _quiz_contador.get(gid, 0) + 1
    num = _quiz_contador[gid]
    escolha = random.choice(disponiveis)
    perguntas_usadas[gid].append(escolha)

    embed = discord.Embed(
        title=f"🎯 Quiz Valorant — Pergunta #{num}",
        description=f"## {escolha['pergunta']}",
        color=COR_NEUTRO
    )
    embed.add_field(name="​", value=f"⏱️ **30 segundos** para responder", inline=False)
    embed.set_footer(text=ft(f"{len(disponiveis)-1} perguntas restantes no banco"))
    await ctx.send(embed=embed)

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    uid = str(ctx.author.id)
    try:
        resposta = await bot.wait_for("message", check=check, timeout=30)
        if not quiz_ativo.get(gid):
            return

        if resposta.content.lower().strip() == escolha["resposta"].lower():
            dados = carregar_xp()
            if uid in dados:
                dados[uid]["xp"] += 15
                salvar_xp(dados)
            stats = get_stats_user(uid)
            stats[uid]["quiz_acertos"] += 1
            stats[uid]["quiz_streak"] = stats[uid].get("quiz_streak", 0) + 1
            salvar_stats(stats)

            embed_ok = discord.Embed(
                title="✅ Resposta Correta!",
                description=f"Muito bem, {ctx.author.mention}! **+15 XP** 🎉",
                color=COR_SUCESSO
            )
            embed_ok.add_field(name="🔥 Sequência", value=f"**{stats[uid]['quiz_streak']}** acerto(s) seguido(s)", inline=True)
            embed_ok.set_footer(text=ft())
            await ctx.send(embed=embed_ok)
            await verificar_conquistas(ctx, uid)
        else:
            # Mostra curiosidade se disponível
            curiosidade = CURIOSIDADES.get(escolha["resposta"].lower(), "")
            desc = f"A resposta correta era: **{escolha['resposta']}**"
            if curiosidade:
                desc += f"\n\n{curiosidade}"

            stats = get_stats_user(uid)
            stats[uid]["quiz_streak"] = 0
            salvar_stats(stats)

            embed_err = discord.Embed(
                title="❌ Resposta Errada!",
                description=desc,
                color=COR_PADRAO
            )
            embed_err.set_footer(text=ft())
            await ctx.send(embed=embed_err)
    except asyncio.TimeoutError:
        embed_to = discord.Embed(
            title="⏰ Tempo Esgotado!",
            description=f"A resposta era: **{escolha['resposta']}**",
            color=COR_PADRAO
        )
        embed_to.set_footer(text=ft())
        await ctx.send(embed=embed_to)
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
# RANK, TOP e RANKGLOBAL
# ============================================================
@bot.command()
@requer_acesso()
async def rank(ctx):
    dados = carregar_xp()
    uid   = str(ctx.author.id)
    if uid not in dados:
        await ctx.send("❌ Você ainda não tem XP! Mande uma mensagem para começar.")
        return

    xp     = dados[uid]["xp"]
    nivel  = dados[uid]["nivel"]
    proximo = nivel * 100
    progresso = barra_progresso(xp % 100, 100, 15)

    # Posição no ranking global
    ranking = sorted(dados.items(), key=lambda x: x[1].get("xp", 0), reverse=True)
    posicao = next((i+1 for i, (k, _) in enumerate(ranking) if k == uid), "—")

    embed = discord.Embed(
        title=f"📊 Ranking — {ctx.author.display_name}",
        color=COR_NEUTRO
    )
    embed.add_field(name="🎖️ Nível",    value=f"**{nivel}**",       inline=True)
    embed.add_field(name="⭐ XP Total", value=f"**{xp}**",           inline=True)
    embed.add_field(name="🥇 Posição",  value=f"**#{posicao}**",     inline=True)
    embed.add_field(name="📈 Progresso para o próximo nível",
                    value=f"`{progresso}` **{xp % 100}/100 XP**", inline=False)
    if ctx.author.avatar:
        embed.set_thumbnail(url=ctx.author.avatar.url)
    embed.set_footer(text=ft())
    await ctx.send(embed=embed)

@bot.command()
@requer_acesso()
async def top(ctx):
    dados = carregar_xp()
    if not dados:
        await ctx.send("⚠️ Ninguém tem XP ainda!")
        return
    ranking = sorted(dados.items(), key=lambda x: x[1].get("xp", 0), reverse=True)[:5]
    total_xp = sum(v.get("xp", 0) for v in dados.values())
    media_xp = round(total_xp / max(len(dados), 1))

    embed = discord.Embed(
        title="🏆 Top 5 — Ranking Global",
        color=COR_OURO
    )
    medalhas = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
    for i, (user_id, info) in enumerate(ranking):
        try:
            usuario = await bot.fetch_user(int(user_id))
            nome = usuario.display_name
        except:
            nome = f"Jogador {user_id[-4:]}"
        embed.add_field(
            name=f"{medalhas[i]} {nome}",
            value=f"Nível **{info.get('nivel', 1)}** • **{info.get('xp', 0):,}** XP",
            inline=False
        )
    embed.add_field(name="​", value="​", inline=False)
    embed.add_field(name="📊 XP Total Acumulado", value=f"**{total_xp:,}**", inline=True)
    embed.add_field(name="📉 Média por Jogador",  value=f"**{media_xp:,}**", inline=True)
    embed.set_footer(text=ft(f"{len(dados)} jogadores registrados"))
    await ctx.send(embed=embed)

@bot.command()
@requer_acesso()
async def rankglobal(ctx):
    """Top 3 de todos os servidores combinados."""
    dados = carregar_xp()
    if not dados:
        await ctx.send("⚠️ Ninguém tem XP ainda!")
        return
    ranking = sorted(dados.items(), key=lambda x: x[1].get("xp", 0), reverse=True)[:3]

    embed = discord.Embed(
        title="🌍 Top 3 Global — Todos os Servidores",
        description="Os maiores jogadores de **todos** os servidores ValBot combinados",
        color=COR_OURO
    )
    medalhas = ["🥇", "🥈", "🥉"]
    for i, (user_id, info) in enumerate(ranking):
        try:
            usuario = await bot.fetch_user(int(user_id))
            nome = usuario.display_name
            avatar = usuario.avatar.url if usuario.avatar else None
        except:
            nome  = f"Jogador {user_id[-4:]}"
            avatar = None
        embed.add_field(
            name=f"{medalhas[i]} {nome}",
            value=f"Nível **{info.get('nivel', 1)}** • **{info.get('xp', 0):,}** XP",
            inline=False
        )
        if i == 0 and avatar:
            embed.set_thumbnail(url=avatar)
    embed.set_footer(text=ft(f"{len(dados)} jogadores no ranking global"))
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

    fim = datetime.now(timezone.utc) + timedelta(seconds=tempo)
    embed = discord.Embed(
        title="🎁 ✨ SORTEIO ATIVO! ✨ 🎁",
        description=(
            f"**🎀 Prêmio:** {premio}\n\n"
            f"Reaja com 🎉 para participar!\n"
            f"⏰ Encerra: <t:{int(fim.timestamp())}:R>"
        ),
        color=COR_OURO
    )
    embed.set_footer(text=ft(f"Criado por {ctx.author.display_name}"))
    mensagem = await ctx.send(embed=embed)
    await mensagem.add_reaction("🎉")
    await asyncio.sleep(tempo)

    mensagem = await ctx.channel.fetch_message(mensagem.id)
    usuarios = []
    for reacao in mensagem.reactions:
        if str(reacao.emoji) == "🎉":
            async for u in reacao.users():
                if not u.bot:
                    usuarios.append(u)

    if not usuarios:
        await ctx.send(embed=discord.Embed(
            title="😢 Sorteio Encerrado",
            description="Ninguém participou do sorteio.",
            color=COR_PADRAO
        ))
        return

    vencedor = random.choice(usuarios)
    embed_res = discord.Embed(
        title="🏆 🎉 TEMOS UM VENCEDOR! 🎉 🏆",
        description=(
            f"Parabéns {vencedor.mention}!\n"
            f"Você ganhou **{premio}**! 🎊"
        ),
        color=COR_OURO
    )
    embed_res.add_field(name="👥 Participantes", value=f"**{len(usuarios)}**", inline=True)
    embed_res.add_field(name="🎁 Prêmio",        value=f"**{premio}**",        inline=True)
    if vencedor.avatar:
        embed_res.set_thumbnail(url=vencedor.avatar.url)
    embed_res.set_footer(text=ft())
    await ctx.send(embed=embed_res)

@sorteio.error
async def sorteio_error(ctx, error):
    if isinstance(error, (commands.BadArgument, commands.MissingRequiredArgument)):
        await ctx.send("❌ Use: `!sorteio [segundos] [prêmio]` — ex: `!sorteio 60 Nitro`")

# ============================================================
# HENRIK API – !stats, !historico, !perfil
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
        await ctx.send("❌ Use: `!stats Nome#TAG`")
        return
    player_name, player_tag = nome.split("#", 1)
    msg = await ctx.send("🔍 Buscando stats...")
    try:
        async with aiohttp.ClientSession() as session:
            status, perfil = await henrik_get(session,
                f"https://api.henrikdev.xyz/valorant/v2/account/{player_name}/{player_tag}")
            if status != 200:
                await msg.edit(content=f"❌ Erro {status}: `{perfil.get('errors', perfil.get('message', 'sem detalhe'))}`")
                return
            regiao = perfil["data"]["region"]
            _, rank_data = await henrik_get(session,
                f"https://api.henrikdev.xyz/valorant/v3/mmr/{regiao}/pc/{player_name}/{player_tag}")

        dados     = perfil["data"]
        rank_info = rank_data.get("data", {})
        nivel      = dados.get("account_level", "?")
        rank_atual = rank_info.get("current", {}).get("tier", {}).get("name", "Sem rank")
        peak_rank  = rank_info.get("highest", {}).get("tier", {}).get("name", "—")
        elo        = rank_info.get("current", {}).get("elo", 0)
        rr         = rank_info.get("current", {}).get("rr", 0)
        progresso  = barra_progresso(rr, 100, 15)
        cor        = cor_por_rank(rank_atual)
        icone      = get_rank_icon(rank_atual)

        embed = discord.Embed(
            title=f"🎮 {player_name}#{player_tag}",
            color=cor
        )
        embed.add_field(name="🏆 Rank Atual",   value=f"**{rank_atual}**",    inline=True)
        embed.add_field(name="📈 Peak Rank",    value=f"**{peak_rank}**",     inline=True)
        embed.add_field(name="🌎 Região",       value=f"**{regiao.upper()}**",inline=True)
        embed.add_field(name="⭐ ELO",          value=f"**{elo}**",           inline=True)
        embed.add_field(name="🎯 RR",           value=f"**{rr}/100**",        inline=True)
        embed.add_field(name="🎮 Nível",        value=f"**{nivel}**",         inline=True)
        embed.add_field(name="📊 Progresso RR",
                        value=f"`{progresso}` **{rr}%**", inline=False)
        if icone:
            embed.set_thumbnail(url=icone)
        embed.set_footer(text=ft("Henrik API"))
        await msg.delete()
        await ctx.send(embed=embed)
    except Exception as e:
        print(f"[ERRO !stats] {type(e).__name__}: {e}")
        await msg.edit(content="❌ Erro ao buscar stats. Tente novamente.")

@bot.command()
@requer_acesso()
async def historico(ctx, *, nome: str):
    if "#" not in nome:
        await ctx.send("❌ Use: `!historico Nome#TAG`")
        return
    player_name, player_tag = nome.split("#", 1)
    msg = await ctx.send("🔍 Buscando histórico...")
    try:
        async with aiohttp.ClientSession() as session:
            status, perfil = await henrik_get(session,
                f"https://api.henrikdev.xyz/valorant/v2/account/{player_name}/{player_tag}")
            if status != 200:
                await msg.edit(content="❌ Jogador não encontrado!")
                return
            regiao = perfil["data"]["region"]
            _, matches_data = await henrik_get(session,
                f"https://api.henrikdev.xyz/valorant/v4/matches/{regiao}/pc/{player_name}/{player_tag}?mode=competitive&size=5")

        partidas = matches_data.get("data", [])
        if not partidas:
            await msg.edit(content="❌ Nenhuma partida encontrada!")
            return

        embed = discord.Embed(
            title=f"📜 Histórico — {player_name}#{player_tag}",
            description="Últimas **5** partidas competitivas",
            color=COR_NEUTRO
        )
        for partida in partidas:
            jogador = next(
                (p for p in partida["players"]
                 if p["name"].lower() == player_name.lower() and p["tag"].lower() == player_tag.lower()),
                None
            )
            if not jogador:
                continue
            mapa    = partida["metadata"]["map"]["name"]
            rtid    = jogador["team_id"]
            ganhou  = any(t["team_id"] == rtid and t["won"] for t in partida.get("teams", []))
            res     = "✅ Vitória" if ganhou else "❌ Derrota"
            sj      = jogador.get("stats", {})
            k, d, a = sj.get("kills", 0), sj.get("deaths", 1), sj.get("assists", 0)
            kda     = round(k / max(d, 1), 2)
            agente  = jogador.get("agent", {}).get("name", "?")
            embed.add_field(
                name=f"{res} — {mapa}",
                value=f"**{agente}** • K/D/A: `{k}/{d}/{a}` • KDA: **{kda}**",
                inline=False
            )
        embed.set_footer(text=ft("Henrik API"))
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
            status, perfil_data = await henrik_get(session,
                f"https://api.henrikdev.xyz/valorant/v2/account/{player_name}/{player_tag}")
            if status != 200:
                await msg.edit(content="❌ Jogador não encontrado!")
                return
            regiao = perfil_data["data"]["region"]
            _, rank_data    = await henrik_get(session,
                f"https://api.henrikdev.xyz/valorant/v3/mmr/{regiao}/pc/{player_name}/{player_tag}")
            _, matches_data = await henrik_get(session,
                f"https://api.henrikdev.xyz/valorant/v4/matches/{regiao}/pc/{player_name}/{player_tag}?mode=competitive&size=10")

        rank_info  = rank_data.get("data", {})
        rank_atual = rank_info.get("current", {}).get("tier", {}).get("name", "Sem rank")
        elo        = rank_info.get("current", {}).get("elo", 0)
        rr         = rank_info.get("current", {}).get("rr", 0)

        partidas = matches_data.get("data", [])
        vit = 0; tot_k = tot_d = tot_a = 0
        agentes_cnt: dict = {}; mapas_cnt: dict = {}
        for partida in partidas:
            jogador = next(
                (p for p in partida["players"]
                 if p["name"].lower() == player_name.lower() and p["tag"].lower() == player_tag.lower()),
                None
            )
            if not jogador:
                continue
            rtid = jogador["team_id"]
            if any(t["team_id"] == rtid and t["won"] for t in partida.get("teams", [])):
                vit += 1
            sj = jogador.get("stats", {})
            tot_k += sj.get("kills", 0); tot_d += sj.get("deaths", 0); tot_a += sj.get("assists", 0)
            ag = jogador.get("agent", {}).get("name", "?")
            mp = partida["metadata"]["map"]["name"]
            agentes_cnt[ag] = agentes_cnt.get(ag, 0) + 1
            mapas_cnt[mp]   = mapas_cnt.get(mp, 0) + 1

        n_part  = max(len(partidas), 1)
        winrate = round((vit / n_part) * 100, 1)
        kda     = round((tot_k + tot_a) / max(tot_d, 1), 2)
        ag_top  = max(agentes_cnt, key=agentes_cnt.get) if agentes_cnt else "—"
        mp_top  = max(mapas_cnt,   key=mapas_cnt.get)   if mapas_cnt   else "—"

        perfis = carregar_perfis()
        uid    = str(ctx.author.id)
        custom = perfis.get(uid, {})
        ag_fav   = custom.get("agente", ag_top)
        arma_fav = custom.get("arma", "—")
        titulo   = custom.get("titulo", "Jogador da Arca")

        perfis.setdefault("_meta", {}).setdefault(str(ctx.guild.id), {})[uid] = ag_top
        salvar_perfis(perfis)

        cor   = cor_por_rank(rank_atual)
        icone = get_rank_icon(rank_atual)

        embed = discord.Embed(
            title=f"🎮 {player_name}#{player_tag}",
            description=f"*{titulo}*",
            color=cor
        )
        # Linha 1: Rank
        embed.add_field(name="🏆 Rank",   value=f"**{rank_atual}**",    inline=True)
        embed.add_field(name="⭐ ELO",    value=f"**{elo}**",           inline=True)
        embed.add_field(name="🎯 RR",     value=f"**{rr}/100**",        inline=True)
        # Linha 2: Performance
        embed.add_field(name="📊 Winrate (10p)", value=f"**{winrate}%**", inline=True)
        embed.add_field(name="🔫 KDA Médio",     value=f"**{kda}**",      inline=True)
        embed.add_field(name="🌎 Região",        value=f"**{regiao.upper()}**", inline=True)
        # Separador
        embed.add_field(name="​", value="​", inline=False)
        # Linha 3: Favoritos
        embed.add_field(name="👤 Agente Favorito",   value=f"**{ag_fav.title()}**",  inline=True)
        embed.add_field(name="🗺️ Mapa Mais Jogado",  value=f"**{mp_top}**",          inline=True)
        embed.add_field(name="🔪 Arma Favorita",     value=f"**{arma_fav.title()}**",inline=True)

        if icone:
            embed.set_thumbnail(url=icone)
        elif (img := get_agent_image(ag_fav)):
            embed.set_thumbnail(url=img)
        embed.set_footer(text=ft("Personalize com !setagente, !setarma, !settitulo"))
        await msg.delete()
        await ctx.send(embed=embed)
    except Exception as e:
        print(f"[ERRO !perfil] {type(e).__name__}: {e}")
        await msg.edit(content="❌ Erro ao montar perfil. Tente novamente.")

@bot.command()
@requer_acesso()
async def setagente(ctx, *, nome: str):
    perfis = carregar_perfis()
    uid = str(ctx.author.id)
    perfis.setdefault(uid, {})["agente"] = nome.strip()
    salvar_perfis(perfis)
    embed = discord.Embed(title="✅ Agente Favorito Definido",
                          description=f"**{nome.title()}**", color=COR_SUCESSO)
    if img := get_agent_image(nome):
        embed.set_thumbnail(url=img)
    embed.set_footer(text=ft())
    await ctx.send(embed=embed)

@bot.command()
@requer_acesso()
async def setarma(ctx, *, nome: str):
    perfis = carregar_perfis()
    uid = str(ctx.author.id)
    perfis.setdefault(uid, {})["arma"] = nome.strip()
    salvar_perfis(perfis)
    embed = discord.Embed(title="✅ Arma Favorita Definida",
                          description=f"**{nome.title()}**", color=COR_SUCESSO)
    embed.set_footer(text=ft())
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
    embed = discord.Embed(title="✅ Título Personalizado Definido",
                          description=f"*{texto}*", color=COR_SUCESSO)
    embed.set_footer(text=ft())
    await ctx.send(embed=embed)

# ============================================================
# SISTEMA DE TIMES
# ============================================================
@bot.command()
@requer_acesso()
async def criartime(ctx, *, nome: str):
    times = carregar_times()
    gid   = str(ctx.guild.id)
    times.setdefault(gid, {})
    nome_l = nome.lower()
    if nome_l in times[gid]:
        await ctx.send("⚠️ Já existe um time com esse nome!")
        return
    uid = str(ctx.author.id)
    for info in times[gid].values():
        if uid in info.get("membros", []):
            info["membros"].remove(uid)
    times[gid][nome_l] = {"nome_display": nome, "lider": uid, "membros": [uid]}
    salvar_times(times)
    embed = discord.Embed(
        title="🛡️ Time Criado!",
        description=f"**{nome}** foi criado por {ctx.author.mention}.\nUse `!entrartime {nome}` para convidar.",
        color=COR_SUCESSO
    )
    embed.set_footer(text=ft())
    await ctx.send(embed=embed)
    await verificar_conquistas(ctx, uid)

@bot.command()
@requer_acesso()
async def entrartime(ctx, *, nome: str):
    times = carregar_times()
    gid   = str(ctx.guild.id)
    times.setdefault(gid, {})
    nome_l = nome.lower()
    if nome_l not in times[gid]:
        await ctx.send("❌ Time não encontrado. Veja `!timelist`.")
        return
    uid = str(ctx.author.id)
    for info in times[gid].values():
        if uid in info.get("membros", []):
            info["membros"].remove(uid)
    times[gid][nome_l]["membros"].append(uid)
    salvar_times(times)
    await ctx.send(f"🤝 {ctx.author.mention} entrou no time **{times[gid][nome_l]['nome_display']}**!")
    await verificar_conquistas(ctx, uid)

@bot.command()
@requer_acesso()
async def sairtime(ctx):
    times  = carregar_times()
    gid    = str(ctx.guild.id)
    uid    = str(ctx.author.id)
    saiu_de = None
    times.setdefault(gid, {})
    for n, info in list(times[gid].items()):
        if uid in info.get("membros", []):
            info["membros"].remove(uid)
            saiu_de = info["nome_display"]
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
    times    = carregar_times()
    gid      = str(ctx.guild.id)
    lst      = times.get(gid, {})
    if not lst:
        await ctx.send("⚠️ Nenhum time criado ainda. Use `!criartime [nome]`.")
        return
    dados_xp = carregar_xp()
    ranking  = sorted(
        [(info["nome_display"], len(info["membros"]),
          sum(dados_xp.get(m, {}).get("xp", 0) for m in info.get("membros", [])))
         for info in lst.values()],
        key=lambda x: x[2], reverse=True
    )
    embed    = discord.Embed(title="🛡️ Ranking de Times", color=COR_NEUTRO)
    medalhas = ["🥇", "🥈", "🥉"] + ["▫️"] * 20
    for i, (n, qtd, xp) in enumerate(ranking):
        embed.add_field(name=f"{medalhas[i]} {n}",
                        value=f"👥 **{qtd}** membros • ⭐ **{xp:,}** XP", inline=False)
    embed.set_footer(text=ft())
    await ctx.send(embed=embed)

@bot.command()
@requer_acesso()
async def timeinfo(ctx, *, nome: str):
    times  = carregar_times()
    gid    = str(ctx.guild.id)
    nome_l = nome.lower()
    if nome_l not in times.get(gid, {}):
        await ctx.send("❌ Time não encontrado.")
        return
    info     = times[gid][nome_l]
    dados_xp = carregar_xp()
    membros_str = ""
    xp_total    = 0
    for m in info["membros"]:
        try:
            u = await bot.fetch_user(int(m))
            n = u.display_name
        except:
            n = f"Jogador {m[-4:]}"
        xp_m = dados_xp.get(m, {}).get("xp", 0)
        xp_total += xp_m
        lider = " 👑" if m == info["lider"] else ""
        membros_str += f"• **{n}**{lider} — {xp_m:,} XP\n"

    embed = discord.Embed(title=f"🛡️ {info['nome_display']}", color=COR_NEUTRO)
    embed.add_field(name="👥 Membros",  value=membros_str or "—",            inline=False)
    embed.add_field(name="⭐ XP Total", value=f"**{xp_total:,}**",           inline=True)
    embed.add_field(name="📦 Tamanho",  value=f"**{len(info['membros'])}**", inline=True)
    embed.set_footer(text=ft())
    await ctx.send(embed=embed)

# ============================================================
# DUELO
# ============================================================
duelos_ativos = {}

@bot.command()
@requer_acesso()
async def duelo(ctx, oponente: discord.Member):
    if oponente.bot or oponente.id == ctx.author.id:
        await ctx.send("⚠️ Escolha outro jogador (não bot e não você mesmo).")
        return
    gid  = str(ctx.guild.id)
    key1 = (gid, ctx.author.id)
    key2 = (gid, oponente.id)
    if duelos_ativos.get(key1) or duelos_ativos.get(key2):
        await ctx.send("⚠️ Um dos jogadores já está em duelo.")
        return
    duelos_ativos[key1] = True
    duelos_ativos[key2] = True

    embed_inicio = discord.Embed(
        title="⚔️  DUELO DE QUIZ  ⚔️",
        description=(
            f"```\n"
            f"  {ctx.author.display_name}\n"
            f"        VS\n"
            f"  {oponente.display_name}\n"
            f"```\n"
            f"**5 perguntas** • Primeiro a responder certo ganha o ponto!\n\n"
            f"{oponente.mention}, digite **`aceitar`** em 30s para entrar na batalha."
        ),
        color=COR_PADRAO
    )
    embed_inicio.set_footer(text=ft())
    await ctx.send(embed=embed_inicio)

    def check_aceite(m):
        return m.author.id == oponente.id and m.channel == ctx.channel and m.content.lower() == "aceitar"
    try:
        await bot.wait_for("message", check=check_aceite, timeout=30)
    except asyncio.TimeoutError:
        await ctx.send(embed=discord.Embed(
            description="⏰ O oponente não aceitou o duelo.",
            color=COR_PADRAO
        ))
        duelos_ativos.pop(key1, None); duelos_ativos.pop(key2, None)
        return

    pontos = {ctx.author.id: 0, oponente.id: 0}
    perguntas_d = random.sample(perguntas_todas, 5)

    for i, q in enumerate(perguntas_d, 1):
        emb_q = discord.Embed(
            title=f"⚔️ Pergunta {i}/5",
            description=f"## {q['pergunta']}\n\n⚡ Primeiro a acertar ganha o ponto! **(20s)**",
            color=COR_NEUTRO
        )
        emb_q.set_footer(text=ft(
            f"{ctx.author.display_name}: {pontos[ctx.author.id]}pt  •  "
            f"{oponente.display_name}: {pontos[oponente.id]}pt"
        ))
        await ctx.send(embed=emb_q)

        def check_q(m):
            return m.author.id in (ctx.author.id, oponente.id) and m.channel == ctx.channel
        try:
            tempo_fim      = asyncio.get_running_loop().time() + 20
            vencedor_rodada = None
            while True:
                restante = tempo_fim - asyncio.get_running_loop().time()
                if restante <= 0:
                    break
                resp = await bot.wait_for("message", check=check_q, timeout=restante)
                if resp.content.lower().strip() == q["resposta"].lower():
                    pontos[resp.author.id] += 1
                    vencedor_rodada = resp.author
                    await ctx.send(f"✅ **{resp.author.display_name}** acertou! **+1 ponto**")
                    break
            if not vencedor_rodada:
                await ctx.send(f"⏰ Ninguém acertou. Resposta: **{q['resposta']}**")
        except asyncio.TimeoutError:
            await ctx.send(f"⏰ Tempo! Resposta: **{q['resposta']}**")

    duelos_ativos.pop(key1, None); duelos_ativos.pop(key2, None)

    p1, p2 = pontos[ctx.author.id], pontos[oponente.id]
    if p1 > p2:   venc, perd = ctx.author, oponente
    elif p2 > p1: venc, perd = oponente, ctx.author
    else:         venc = perd = None

    if venc:
        uid_v, uid_p = str(venc.id), str(perd.id)
        get_stats_user(uid_v); get_stats_user(uid_p)
        stats_all = carregar_stats()
        stats_all[uid_v]["duelos_venc"]         = stats_all[uid_v].get("duelos_venc", 0) + 1
        stats_all[uid_v]["duelos_streak_atual"]  = stats_all[uid_v].get("duelos_streak_atual", 0) + 1
        if stats_all[uid_v]["duelos_streak_atual"] > stats_all[uid_v].get("duelos_streak_max", 0):
            stats_all[uid_v]["duelos_streak_max"] = stats_all[uid_v]["duelos_streak_atual"]
        stats_all[uid_p]["duelos_streak_atual"] = 0
        salvar_stats(stats_all)
        desc = (f"🥇 **Vencedor:** {venc.mention}\n\n"
                f"**{ctx.author.display_name}**: {p1} pts\n"
                f"**{oponente.display_name}**: {p2} pts")
        cor_fim = COR_OURO
        await verificar_conquistas(ctx, uid_v)
    else:
        desc = (f"🤝 **Empate!**\n\n"
                f"**{ctx.author.display_name}**: {p1} pts\n"
                f"**{oponente.display_name}**: {p2} pts")
        cor_fim = COR_NEUTRO

    emb_fim = discord.Embed(title="⚔️ Resultado do Duelo", description=desc, color=cor_fim)
    emb_fim.set_footer(text=ft())
    await ctx.send(embed=emb_fim)

# ============================================================
# MISSÃO DIÁRIA
# ============================================================
MISSOES = [
    {"desc": "Mande 20 mensagens hoje",       "xp": 30, "tipo": "msg",   "alvo": 20},
    {"desc": "Acerte 3 perguntas no !quiz",   "xp": 50, "tipo": "quiz",  "alvo": 3},
    {"desc": "Vença 1 duelo hoje",            "xp": 40, "tipo": "duelo", "alvo": 1},
    {"desc": "Use o bot pelo menos 1 vez",    "xp": 20, "tipo": "msg",   "alvo": 1},
    {"desc": "Mande 50 mensagens hoje",       "xp": 70, "tipo": "msg",   "alvo": 50},
]

@bot.command()
@requer_acesso()
async def missao(ctx):
    uid  = str(ctx.author.id)
    hoje = datetime.now(timezone.utc).strftime("%Y%m%d")
    random.seed(int(hoje) + sum(ord(c) for c in uid))
    m = random.choice(MISSOES)
    random.seed()

    stats = carregar_stats().get(uid, {})
    atual = stats.get("mensagens" if m["tipo"] == "msg" else
                      "quiz_acertos" if m["tipo"] == "quiz" else "duelos_venc", 0)

    progresso = barra_progresso(min(atual, m["alvo"]), m["alvo"], 15)
    completa  = atual >= m["alvo"]

    embed = discord.Embed(
        title="🎯 Missão Diária",
        description=f"**{m['desc']}**\n🎁 Recompensa: **+{m['xp']} XP**",
        color=COR_OURO if completa else COR_NEUTRO
    )
    embed.add_field(name="📊 Progresso",
                    value=f"`{progresso}` **{min(atual, m['alvo'])}/{m['alvo']}**", inline=False)
    embed.add_field(name="🔖 Status",
                    value="✅ **Completa!**" if completa else "🔄 Em andamento", inline=True)

    perfis = carregar_perfis()
    chave  = f"missao_{hoje}"
    if completa and perfis.get(uid, {}).get(chave) != True:
        perfis.setdefault(uid, {})[chave] = True
        salvar_perfis(perfis)
        dados = carregar_xp()
        dados.setdefault(uid, {"xp": 0, "nivel": 1})["xp"] += m["xp"]
        salvar_xp(dados)
        embed.add_field(name="💰 XP Recebido", value=f"**+{m['xp']} XP**", inline=True)
        embed.set_footer(text=ft("XP coletado!"))
    else:
        embed.set_footer(text=ft())
    await ctx.send(embed=embed)

# ============================================================
# META
# ============================================================
@bot.command()
@requer_acesso()
async def meta(ctx):
    perfis = carregar_perfis()
    gid    = str(ctx.guild.id)
    agentes_srv = perfis.get("_meta", {}).get(gid, {})
    if not agentes_srv:
        await ctx.send("⚠️ Ainda ninguém usou `!perfil` neste servidor.")
        return
    cnt  = {}
    for uid, ag in agentes_srv.items():
        cnt[ag] = cnt.get(ag, 0) + 1
    top5 = sorted(cnt.items(), key=lambda x: x[1], reverse=True)[:5]
    embed = discord.Embed(
        title="📊 Meta do Servidor — Top 5 Agentes",
        description="Agentes mais jogados pelos membros (via `!perfil`)",
        color=COR_NEUTRO
    )
    medalhas = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
    for i, (ag, q) in enumerate(top5):
        embed.add_field(name=f"{medalhas[i]} {ag.title()}", value=f"**{q}** jogadores", inline=True)
    if img := get_agent_image(top5[0][0]):
        embed.set_thumbnail(url=img)
    embed.set_footer(text=ft())
    await ctx.send(embed=embed)

# ============================================================
# INFO DO SERVIDOR
# ============================================================
@bot.command()
@requer_acesso()
async def info(ctx):
    dados_xp   = carregar_xp()
    dados_conq = carregar_conquistas()
    dados_times = carregar_times()

    membros_ids    = {str(m.id) for m in ctx.guild.members if not m.bot}
    membros_com_xp = sum(1 for uid in membros_ids if uid in dados_xp)
    total_conq_srv = sum(len(c) for uid, c in dados_conq.items() if uid in membros_ids)
    times_srv      = dados_times.get(str(ctx.guild.id), {})
    num_times      = len(times_srv)
    total_membros  = sum(1 for m in ctx.guild.members if not m.bot)
    xp_srv_total   = sum(dados_xp.get(uid, {}).get("xp", 0) for uid in membros_ids)

    embed = discord.Embed(
        title=f"📋 Informações — {ctx.guild.name}",
        color=COR_NEUTRO
    )
    embed.add_field(name="👥 Membros no Servidor", value=f"**{total_membros}**",      inline=True)
    embed.add_field(name="📊 Com XP Registrado",   value=f"**{membros_com_xp}**",     inline=True)
    embed.add_field(name="⭐ XP Total do Servidor", value=f"**{xp_srv_total:,}**",    inline=True)
    embed.add_field(name="​", value="​", inline=False)
    embed.add_field(name="🏅 Conquistas Desbloqueadas", value=f"**{total_conq_srv}**",inline=True)
    embed.add_field(name="🛡️ Times Ativos",             value=f"**{num_times}**",     inline=True)
    embed.add_field(name="🤖 Versão do Bot",            value=f"**v{VERSAO}**",        inline=True)
    if ctx.guild.icon:
        embed.set_thumbnail(url=ctx.guild.icon.url)
    embed.set_footer(text=ft())
    await ctx.send(embed=embed)

# ============================================================
# CONQUISTAS – comando público
# ============================================================
@bot.command()
@requer_acesso()
async def conquistas(ctx):
    uid  = str(ctx.author.id)
    conq = carregar_conquistas().get(uid, [])

    embed = discord.Embed(
        title=f"🏅 Conquistas — {ctx.author.display_name}",
        color=COR_NEUTRO
    )

    for dif in DIFS_ORDEM:
        grupo = {k: v for k, v in CONQUISTAS.items() if v["dif"] == dif}
        if not grupo:
            continue
        linhas = []
        for chave, info_c in grupo.items():
            marca  = "✅" if chave in conq else "🔒"
            linhas.append(f"{marca} **{info_c['nome']}** — *{info_c['desc']}*")
        embed.add_field(
            name=f"{DIFS_EMOJI[dif]} {dif}",
            value="\n".join(linhas),
            inline=False
        )

    desbloqueadas = len(conq)
    total         = len(CONQUISTAS)
    barra         = barra_progresso(desbloqueadas, total, 15)
    embed.add_field(name="​", value="​", inline=False)
    embed.add_field(name="📊 Progresso Total",
                    value=f"`{barra}` **{desbloqueadas}/{total}**", inline=False)
    if ctx.author.avatar:
        embed.set_thumbnail(url=ctx.author.avatar.url)
    embed.set_footer(text=ft())
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
        description="Últimas atualizações do bot:",
        color=COR_NEUTRO
    )
    for nota in notas[:5]:
        mudancas = "\n".join(f"• {m}" for m in nota.get("mudancas", []))
        embed.add_field(
            name=f"v{nota['versao']} — {nota['data']}",
            value=mudancas[:1020] + ("..." if len(mudancas) > 1020 else ""),
            inline=False
        )
    embed.set_footer(text=ft())
    await ctx.send(embed=embed)

# ============================================================
# AJUDA
# ============================================================
@bot.command()
async def ajuda(ctx):
    embed = discord.Embed(
        title="📚 ValBot — Central de Comandos",
        description=f"Todos os comandos disponíveis • **v{VERSAO}**",
        color=COR_NEUTRO
    )
    embed.add_field(
        name="🎮  Diversão & Quiz",
        value=(
            "`!quiz` — Pergunta de Valorant *(+15 XP)*\n"
            "`!stopquiz` — Cancela o quiz ativo\n"
            "`!duelo @user` — Quiz 1v1 melhor de 5\n"
            "`!sorteio [seg] [prêmio]` — Sorteio com reação\n"
            "`!missao` — Missão diária com recompensa"
        ),
        inline=False
    )
    embed.add_field(name="​", value="​", inline=False)
    embed.add_field(
        name="📊  Stats & Ranking",
        value=(
            "`!rank` — Seu XP, nível e posição\n"
            "`!top` — Top 5 do servidor\n"
            "`!rankglobal` — Top 3 de todos os servidores\n"
            "`!stats Nome#TAG` — Stats da Riot API\n"
            "`!historico Nome#TAG` — Últimas 5 partidas\n"
            "`!perfil Nome#TAG` — Perfil completo com winrate/KDA\n"
            "`!meta` — Top 5 agentes do servidor"
        ),
        inline=False
    )
    embed.add_field(name="​", value="​", inline=False)
    embed.add_field(
        name="🎨  Personalização",
        value=(
            "`!setagente [nome]` — Define agente favorito\n"
            "`!setarma [nome]` — Define arma/skin favorita\n"
            "`!settitulo [texto]` — Título personalizado"
        ),
        inline=False
    )
    embed.add_field(name="​", value="​", inline=False)
    embed.add_field(
        name="🛡️  Times",
        value=(
            "`!criartime [nome]` — Cria um time\n"
            "`!entrartime [nome]` — Entra em um time\n"
            "`!sairtime` — Sai do time atual\n"
            "`!timelist` — Ranking dos times\n"
            "`!timeinfo [nome]` — Detalhes do time"
        ),
        inline=False
    )
    embed.add_field(name="​", value="​", inline=False)
    embed.add_field(
        name="ℹ️  Servidor & Outros",
        value=(
            "`!info` — Estatísticas do servidor\n"
            "`!conquistas` — Suas conquistas desbloqueadas\n"
            "`!patchnotes` — Últimas atualizações\n"
            "`!ping` — Latência do bot"
        ),
        inline=False
    )
    embed.set_footer(text=f"ValBot por Arca • R$ 40/mês • https://discord.gg/VKHG6MFh")
    await ctx.send(embed=embed)

# ============================================================
# RUN
# ============================================================
bot.run(TOKEN)
