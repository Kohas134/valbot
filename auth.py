import json
import os

ARQUIVO_AUTH = "autorizados.json"

# Servidores com acesso gratuito permanente (nunca precisam estar no autorizados.json)
SERVIDORES_GRATUITOS = [
    "1511754478913720410",  # Arca Oficial
]

def carregar_autorizados():
    if os.path.exists(ARQUIVO_AUTH):
        with open(ARQUIVO_AUTH, "r") as f:
            return json.load(f)
    return []

def salvar_autorizados(lista):
    with open(ARQUIVO_AUTH, "w") as f:
        json.dump(lista, f)

def servidor_autorizado(guild_id):
    if str(guild_id) in SERVIDORES_GRATUITOS:
        return True
    return str(guild_id) in carregar_autorizados()

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