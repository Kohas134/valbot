"""
admin.py — Painel administrativo local do ValBot (Arca)
Roda apenas no computador do dono. Nunca suba este arquivo para o Railway.
"""

import json
import os

ARQUIVO_AUTH = "autorizados.json"


def carregar_autorizados():
    if os.path.exists(ARQUIVO_AUTH):
        with open(ARQUIVO_AUTH, "r") as f:
            return json.load(f)
    return []


def salvar_autorizados(lista):
    with open(ARQUIVO_AUTH, "w") as f:
        json.dump(lista, f, indent=2)


def autorizar_servidor(servidor_id):
    autorizados = carregar_autorizados()
    sid = str(servidor_id).strip()
    if sid in autorizados:
        print(f"⚠️  Servidor {sid} já está autorizado.")
        return
    autorizados.append(sid)
    salvar_autorizados(autorizados)
    print(f"✅  Servidor {sid} autorizado com sucesso!")


def desautorizar_servidor(servidor_id):
    autorizados = carregar_autorizados()
    sid = str(servidor_id).strip()
    if sid not in autorizados:
        print(f"⚠️  Servidor {sid} não encontrado na lista.")
        return
    autorizados.remove(sid)
    salvar_autorizados(autorizados)
    print(f"❌  Servidor {sid} removido com sucesso!")


def listar_servidores():
    autorizados = carregar_autorizados()
    print("\n📋  Servidores autorizados (pagantes):")
    if not autorizados:
        print("   (nenhum servidor na lista)")
    else:
        for i, sid in enumerate(autorizados, 1):
            print(f"   {i}. {sid}")
    print(f"\n🔒  Servidores gratuitos permanentes:")
    print("   1. 1511754478913720410  (Arca Oficial)")


def mostrar_menu():
    print("\n" + "=" * 45)
    print("   🎮  ValBot — Painel Admin (Arca)")
    print("=" * 45)
    print("  1. Autorizar servidor")
    print("  2. Desautorizar servidor")
    print("  3. Listar servidores autorizados")
    print("  4. Sair")
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

        elif opcao == "4":
            print("👋  Saindo do painel admin.")
            break

        else:
            print("⚠️  Opção inválida. Escolha entre 1 e 4.")


if __name__ == "__main__":
    # Garante que o arquivo existe antes de começar
    if not os.path.exists(ARQUIVO_AUTH):
        salvar_autorizados([])
        print(f"📁  Arquivo {ARQUIVO_AUTH} criado.")

    try:
        menu()
    except KeyboardInterrupt:
        print("\n👋  Painel encerrado.")
