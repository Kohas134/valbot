import json
import os
from datetime import datetime, timezone

ARQUIVO_AUTH    = "autorizados.json"
ARQUIVO_TESTES  = "testes.json"
ARQUIVO_PAGANTES = "pagantes.json"

# Servidores com acesso gratuito permanente — nunca precisam estar no autorizados.json
SERVIDORES_GRATUITOS = [
    "1511754478913720410",  # Arca Oficial
]

# ── Permanentes ───────────────────────────────────────────────────────────────

def carregar_autorizados():
    if os.path.exists(ARQUIVO_AUTH):
        with open(ARQUIVO_AUTH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def salvar_autorizados(lista):
    with open(ARQUIVO_AUTH, "w", encoding="utf-8") as f:
        json.dump(lista, f, indent=2, ensure_ascii=False)

def autorizar_servidor(guild_id):
    autorizados = carregar_autorizados()
    if str(guild_id) not in autorizados:
        autorizados.append(str(guild_id))
        salvar_autorizados(autorizados)
        return True
    return False

def desautorizar_servidor(guild_id):
    autorizados = carregar_autorizados()
    if str(guild_id) in autorizados:
        autorizados.remove(str(guild_id))
        salvar_autorizados(autorizados)
        return True
    return False

# ── Pagantes (assinatura mensal) ──────────────────────────────────────────────

def carregar_pagantes():
    if os.path.exists(ARQUIVO_PAGANTES):
        with open(ARQUIVO_PAGANTES, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def salvar_pagantes(dados):
    with open(ARQUIVO_PAGANTES, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)

def dias_restantes_pagante(guild_id):
    """Retorna dias restantes (float) ou None se não for pagante."""
    pagantes = carregar_pagantes()
    sid = str(guild_id)
    if sid not in pagantes:
        return None
    exp = datetime.fromisoformat(pagantes[sid]["expiracao"])
    if exp.tzinfo is None:
        exp = exp.replace(tzinfo=timezone.utc)
    return (exp - datetime.now(timezone.utc)).total_seconds() / 86400

# ── Testes gratuitos ──────────────────────────────────────────────────────────

def carregar_testes():
    if os.path.exists(ARQUIVO_TESTES):
        with open(ARQUIVO_TESTES, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def salvar_testes(dados):
    with open(ARQUIVO_TESTES, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)

# ── Status central ────────────────────────────────────────────────────────────

def status_servidor(guild_id):
    """
    Retorna:
      "autorizado"  — gratuito permanente, permanente manual ou pagante ativo
      "expirado"    — assinatura mensal vencida  OU  teste vencido
      "negado"      — não está em nenhuma lista
    """
    sid = str(guild_id)

    if sid in SERVIDORES_GRATUITOS:
        return "autorizado"

    if sid in carregar_autorizados():
        return "autorizado"

    # Pagante com assinatura mensal
    pagantes = carregar_pagantes()
    if sid in pagantes:
        dias = dias_restantes_pagante(sid)
        return "autorizado" if dias > 0 else "expirado"

    # Teste gratuito de 3 dias
    testes = carregar_testes()
    if sid in testes:
        inicio = datetime.fromisoformat(testes[sid]["inicio"])
        if inicio.tzinfo is None:
            inicio = inicio.replace(tzinfo=timezone.utc)
        horas = (datetime.now(timezone.utc) - inicio).total_seconds() / 3600
        return "autorizado" if horas < 72 else "expirado"

    return "negado"

def servidor_autorizado(guild_id):
    return status_servidor(guild_id) == "autorizado"
