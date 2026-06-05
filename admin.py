"""
admin.py — Painel administrativo local do ValBot (Arca)
Roda apenas no computador do dono. Nunca suba este arquivo para o Railway.

Ao autorizar ou desautorizar um servidor, o admin.py edita o autorizados.json
e faz push automático para o GitHub — o Railway faz redeploy com a lista atualizada.
"""

import json
import os
import subprocess
from datetime import datetime, timezone

ARQUIVO_AUTH = "autorizados.json"
ARQUIVO_TESTES = "testes.json"

# Diretório onde este script está (raiz do repositório)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# ── Utilitários de arquivo ────────────────────────────────────────────────────

def carregar_autorizados():
    caminho = os.path.join(BASE_DIR, ARQUIVO_AUTH)
    if not os.path.exists(caminho):
        salvar_autorizados([])
        return []
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            conteudo = f.read().strip()
            if not conteudo:
                salvar_autorizados([])
                return []
            return json.loads(conteudo)
    except json.JSONDecodeError:
        print("⚠️  autorizados.json corrompido — recriando vazio.")
        salvar_autorizados([])
        return []


def salvar_autorizados(lista):
    caminho = os.path.join(BASE_DIR, ARQUIVO_AUTH)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(lista, f, indent=2)


def git_push_autorizados():
    """Faz commit e push do autorizados.json para o GitHub."""
    print("  📤  Enviando para o GitHub...")
    try:
        subprocess.run(
            ["git", "add", ARQUIVO_AUTH],
            cwd=BASE_DIR, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "atualiza servidores autorizados"],
            cwd=BASE_DIR, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "push"],
            cwd=BASE_DIR, check=True, capture_output=True
        )
        print("  ✅  Push feito! Railway vai atualizar automaticamente.\n")
    except subprocess.CalledProcessError as e:
        print(f"  ⚠️  Erro no git: {e.stderr.decode().strip()}")
        print("  → Faça o push manualmente: git add autorizados.json && git commit -m 'atualiza' && git push\n")


# ── Servidores pagantes ───────────────────────────────────────────────────────

def autorizar_servidor(servidor_id):
    autorizados = carregar_autorizados()
    sid = str(servidor_id).strip()
    if sid in autorizados:
        print(f"⚠️  Servidor {sid} já está autorizado.\n")
        return
    autorizados.append(sid)
    salvar_autorizados(autorizados)
    print(f"✅  Servidor {sid} adicionado ao autorizados.json.")
    git_push_autorizados()


def desautorizar_servidor(servidor_id):
    autorizados = carregar_autorizados()
    sid = str(servidor_id).strip()
    if sid not in autorizados:
        print(f"⚠️  Servidor {sid} não encontrado na lista.\n")
        return
    autorizados.remove(sid)
    salvar_autorizados(autorizados)
    print(f"❌  Servidor {sid} removido do autorizados.json.")
    git_push_autorizados()


def listar_servidores():
    autorizados = carregar_autorizados()
    print("\n📋  Servidores autorizados (pagantes):")
    if not autorizados:
        print("   (nenhum servidor na lista)")
    else:
        for i, sid in enumerate(autorizados, 1):
            print(f"   {i}. {sid}")
    print("\n🔒  Servidores gratuitos permanentes (hardcoded):")
    print("   • 1511754478913720410  (Arca Oficial)\n")


# ── Testes gratuitos ─────────────────────────────────────────────────────────

def carregar_testes():
    caminho = os.path.join(BASE_DIR, ARQUIVO_TESTES)
    if os.path.exists(caminho):
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def salvar_testes(dados):
    caminho = os.path.join(BASE_DIR, ARQUIVO_TESTES)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2)


def iniciar_teste(servidor_id):
    testes = carregar_testes()
    sid = str(servidor_id).strip()
    if sid in testes:
        inicio = datetime.fromisoformat(testes[sid]["inicio"])
        if inicio.tzinfo is None:
            inicio = inicio.replace(tzinfo=timezone.utc)
        horas = (datetime.now(timezone.utc) - inicio).total_seconds() / 3600
        if horas < 72:
            restam = round(72 - horas, 1)
            print(f"⚠️  Servidor {sid} já está em teste. Restam {restam}h.\n")
            return
    testes[sid] = {
        "inicio": datetime.now(timezone.utc).isoformat(),
        "aviso_enviado": False,
    }
    salvar_testes(testes)
    print(f"✅  Teste gratuito de 3 dias iniciado para o servidor {sid}!\n")


def listar_testes():
    testes = carregar_testes()
    print("\n🧪  Servidores em teste gratuito:")
    if not testes:
        print("   (nenhum servidor em teste)")
        return
    agora = datetime.now(timezone.utc)
    for i, (sid, info) in enumerate(testes.items(), 1):
        inicio = datetime.fromisoformat(info["inicio"])
        if inicio.tzinfo is None:
            inicio = inicio.replace(tzinfo=timezone.utc)
        horas_passadas = (agora - inicio).total_seconds() / 3600
        restam = 72 - horas_passadas
        status = f"✅ Ativo — {round(restam, 1)}h restantes" if restam > 0 else "❌ Expirado"
        print(f"   {i}. {sid}  |  {status}")
    print()


# ── Menu ─────────────────────────────────────────────────────────────────────

def mostrar_menu():
    print("\n" + "=" * 45)
    print("   🎮  ValBot — Painel Admin (Arca)")
    print("=" * 45)
    print("  1. Autorizar servidor")
    print("  2. Desautorizar servidor")
    print("  3. Listar servidores autorizados")
    print("  ─────────────────────────────────────────")
    print("  5. Iniciar teste gratuito (3 dias)")
    print("  6. Listar servidores em teste")
    print("  ─────────────────────────────────────────")
    print("  7. Sair")
    print("=" * 45)


def menu():
    while True:
        mostrar_menu()
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            sid = input("ID do servidor a autorizar: ").strip()
            if sid:
                autorizar_servidor(sid)
            else:
                print("⚠️  ID inválido.")

        elif opcao == "2":
            sid = input("ID do servidor a desautorizar: ").strip()
            if sid:
                desautorizar_servidor(sid)
            else:
                print("⚠️  ID inválido.")

        elif opcao == "3":
            listar_servidores()

        elif opcao == "5":
            sid = input("ID do servidor para iniciar o teste: ").strip()
            if sid:
                iniciar_teste(sid)
            else:
                print("⚠️  ID inválido.")

        elif opcao == "6":
            listar_testes()

        elif opcao == "7":
            print("👋  Saindo do painel admin.")
            break

        else:
            print("⚠️  Opção inválida. Escolha 1, 2, 3, 5, 6 ou 7.")


if __name__ == "__main__":
    try:
        menu()
    except KeyboardInterrupt:
        print("\n👋  Painel encerrado.")
