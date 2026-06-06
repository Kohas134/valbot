import json
import os
from datetime import datetime, timezone

ARQUIVO_AUTH = "autorizados.json"
ARQUIVO_TESTES = "testes.json"

# Servidores com acesso gratuito permanente — nunca precisam estar no autorizados.json
SERVIDORES_GRATUITOS = [
    "1511754478913720410",  # Arca Oficial
]

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

def carregar_testes():
    if os.path.exists(ARQUIVO_TESTES):
        with open(ARQUIVO_TESTES, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def salvar_testes(dados):
    with open(ARQUIVO_TESTES, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)

def status_servidor(guild_id):
    """
    Retorna:
      "autorizado" — gratuito permanente, pagante ou teste ativo
      "expirado"   — estava em teste mas as 72h passaram
      "negado"     — não está em nenhuma lista
    """
    sid = str(guild_id)
    if sid in SERVIDORES_GRATUITOS:
        return "autorizado"
    if sid in carregar_autorizados():
        return "autorizado"
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