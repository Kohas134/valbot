"""
admin.py — Painel administrativo local do ValBot (Arca)
Roda apenas no computador do dono. Nunca suba este arquivo para o Railway.
"""

import json
import os
import subprocess
from datetime import datetime, timezone, timedelta

ARQUIVO_AUTH     = "autorizados.json"
ARQUIVO_TESTES   = "testes.json"
ARQUIVO_PAGANTES = "pagantes.json"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# ── Utilitários de arquivo ────────────────────────────────────────────────────

def _caminho(nome):
    return os.path.join(BASE_DIR, nome)

def _ler_json(nome, padrao):
    c = _caminho(nome)
    if not os.path.exists(c):
        return padrao
    try:
        with open(c, "r", encoding="utf-8-sig") as f:
            conteudo = f.read().strip()
            return json.loads(conteudo) if conteudo else padrao
    except (json.JSONDecodeError, UnicodeDecodeError):
        print(f"⚠️  {nome} corrompido — recriando vazio.")
        return padrao

def _salvar_json(nome, dados):
    with open(_caminho(nome), "w", encoding="utf-8", newline="\n") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)


def git_push(*arquivos):
    """Faz commit e push dos arquivos informados."""
    print("  📤  Enviando para o GitHub...")
    try:
        subprocess.run(["git", "add"] + list(arquivos),
                       cwd=BASE_DIR, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "atualiza acesso de servidores"],
                       cwd=BASE_DIR, check=True, capture_output=True)
        subprocess.run(["git", "push"],
                       cwd=BASE_DIR, check=True, capture_output=True)
        print("  ✅  Push feito! Railway vai atualizar automaticamente.\n")
    except subprocess.CalledProcessError as e:
        stderr = e.stderr.decode(errors="replace").strip()
        print(f"  ⚠️  Erro no git: {stderr}")
        print(f"  → Faça push manualmente: git add {' '.join(arquivos)} && git commit -m 'atualiza' && git push\n")


# ── Permanentes ───────────────────────────────────────────────────────────────

def carregar_autorizados():
    return _ler_json(ARQUIVO_AUTH, [])

def salvar_autorizados(lista):
    _salvar_json(ARQUIVO_AUTH, lista)

def autorizar_permanente(servidor_id):
    autorizados = carregar_autorizados()
    sid = str(servidor_id).strip()
    if sid in autorizados:
        print(f"⚠️  Servidor {sid} já está permanente.\n")
        return
    autorizados.append(sid)
    salvar_autorizados(autorizados)
    print(f"✅  Servidor {sid} autorizado permanentemente.")
    git_push(ARQUIVO_AUTH)

def desautorizar_permanente(servidor_id):
    autorizados = carregar_autorizados()
    sid = str(servidor_id).strip()
    if sid not in autorizados:
        print(f"⚠️  Servidor {sid} não está na lista permanente.\n")
        return
    autorizados.remove(sid)
    salvar_autorizados(autorizados)
    print(f"❌  Servidor {sid} removido da lista permanente.")
    git_push(ARQUIVO_AUTH)

def listar_permanentes():
    autorizados = carregar_autorizados()
    print("\n♾️   Servidores com acesso permanente (manual):")
    if not autorizados:
        print("   (nenhum)")
    else:
        for i, sid in enumerate(autorizados, 1):
            print(f"   {i}. {sid}")
    print("\n🔒  Gratuitos hardcoded:")
    print("   • 1511754478913720410  (Arca Oficial)\n")


# ── Pagantes (assinatura mensal) ──────────────────────────────────────────────

def carregar_pagantes():
    return _ler_json(ARQUIVO_PAGANTES, {})

def salvar_pagantes(dados):
    _salvar_json(ARQUIVO_PAGANTES, dados)

def registrar_pagamento(servidor_id):
    """
    Adiciona 30 dias ao servidor.
    - Novo servidor   → expira em agora + 30 dias
    - Renovação ativa → empilha 30 dias a partir da expiração atual
    - Renovação após vencimento → expira em agora + 30 dias
    """
    pagantes = carregar_pagantes()
    sid = str(servidor_id).strip()
    agora = datetime.now(timezone.utc)

    if sid in pagantes:
        exp_atual = datetime.fromisoformat(pagantes[sid]["expiracao"])
        if exp_atual.tzinfo is None:
            exp_atual = exp_atual.replace(tzinfo=timezone.utc)
        base = exp_atual if exp_atual > agora else agora
        nova_exp = base + timedelta(days=30)
        pagantes[sid]["expiracao"] = nova_exp.isoformat()
        pagantes[sid]["aviso_enviado"] = False
        dias_restantes = (nova_exp - agora).days
        print(f"✅  +30 dias adicionados ao servidor {sid}.")
        print(f"   Nova expiração: {nova_exp.strftime('%d/%m/%Y')} ({dias_restantes} dias restantes)\n")
    else:
        nova_exp = agora + timedelta(days=30)
        pagantes[sid] = {
            "expiracao": nova_exp.isoformat(),
            "aviso_enviado": False,
        }
        print(f"✅  Servidor {sid} ativado com 30 dias.")
        print(f"   Expira em: {nova_exp.strftime('%d/%m/%Y')}\n")

    salvar_pagantes(pagantes)
    git_push(ARQUIVO_PAGANTES)

def remover_pagante(servidor_id):
    pagantes = carregar_pagantes()
    sid = str(servidor_id).strip()
    if sid not in pagantes:
        print(f"⚠️  Servidor {sid} não está na lista de pagantes.\n")
        return
    del pagantes[sid]
    salvar_pagantes(pagantes)
    print(f"❌  Servidor {sid} removido dos pagantes.")
    git_push(ARQUIVO_PAGANTES)

def listar_pagantes():
    pagantes = carregar_pagantes()
    print("\n💳  Servidores pagantes (assinatura mensal):")
    if not pagantes:
        print("   (nenhum)")
        print()
        return
    agora = datetime.now(timezone.utc)
    for i, (sid, info) in enumerate(pagantes.items(), 1):
        exp = datetime.fromisoformat(info["expiracao"])
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        dias = (exp - agora).days
        if dias > 0:
            status = f"✅ Ativo — expira em {exp.strftime('%d/%m/%Y')} ({dias}d restantes)"
        else:
            status = f"❌ Expirado desde {exp.strftime('%d/%m/%Y')}"
        print(f"   {i}. {sid}  |  {status}")
    print()


# ── Testes gratuitos ──────────────────────────────────────────────────────────

def carregar_testes():
    return _ler_json(ARQUIVO_TESTES, {})

def salvar_testes(dados):
    _salvar_json(ARQUIVO_TESTES, dados)

def iniciar_teste(servidor_id):
    testes = carregar_testes()
    sid = str(servidor_id).strip()
    if sid in testes:
        inicio = datetime.fromisoformat(testes[sid]["inicio"])
        if inicio.tzinfo is None:
            inicio = inicio.replace(tzinfo=timezone.utc)
        horas = (datetime.now(timezone.utc) - inicio).total_seconds() / 3600
        if horas < 72:
            print(f"⚠️  Servidor {sid} já está em teste. Restam {round(72 - horas, 1)}h.\n")
            return
    testes[sid] = {
        "inicio": datetime.now(timezone.utc).isoformat(),
        "aviso_enviado": False,
    }
    salvar_testes(testes)
    print(f"✅  Teste gratuito de 3 dias iniciado para {sid}!\n")

def listar_testes():
    testes = carregar_testes()
    print("\n🧪  Servidores em teste gratuito (3 dias):")
    if not testes:
        print("   (nenhum)")
        print()
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


# ── Menu ──────────────────────────────────────────────────────────────────────

def mostrar_menu():
    print("\n" + "=" * 50)
    print("   🎮  ValBot — Painel Admin (Arca)")
    print("=" * 50)
    print("  💳  ASSINATURA MENSAL")
    print("  1. Registrar pagamento (+1 mês)")
    print("  2. Listar pagantes")
    print("  3. Remover pagante")
    print("  ──────────────────────────────────────────────")
    print("  ♾️   ACESSO PERMANENTE (manual)")
    print("  4. Autorizar servidor permanente")
    print("  5. Desautorizar servidor permanente")
    print("  6. Listar servidores permanentes")
    print("  ──────────────────────────────────────────────")
    print("  🧪  TESTE GRATUITO (3 dias)")
    print("  7. Iniciar teste gratuito")
    print("  8. Listar servidores em teste")
    print("  ──────────────────────────────────────────────")
    print("  9. Sair")
    print("=" * 50)


def menu():
    while True:
        mostrar_menu()
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            sid = input("ID do servidor (registrar pagamento +1 mês): ").strip()
            if sid:
                registrar_pagamento(sid)
            else:
                print("⚠️  ID inválido.")

        elif opcao == "2":
            listar_pagantes()

        elif opcao == "3":
            sid = input("ID do servidor a remover dos pagantes: ").strip()
            if sid:
                remover_pagante(sid)
            else:
                print("⚠️  ID inválido.")

        elif opcao == "4":
            sid = input("ID do servidor a autorizar permanentemente: ").strip()
            if sid:
                autorizar_permanente(sid)
            else:
                print("⚠️  ID inválido.")

        elif opcao == "5":
            sid = input("ID do servidor a desautorizar: ").strip()
            if sid:
                desautorizar_permanente(sid)
            else:
                print("⚠️  ID inválido.")

        elif opcao == "6":
            listar_permanentes()

        elif opcao == "7":
            sid = input("ID do servidor para iniciar o teste: ").strip()
            if sid:
                iniciar_teste(sid)
            else:
                print("⚠️  ID inválido.")

        elif opcao == "8":
            listar_testes()

        elif opcao == "9":
            print("👋  Saindo do painel admin.")
            break

        else:
            print("⚠️  Opção inválida.")


if __name__ == "__main__":
    try:
        menu()
    except KeyboardInterrupt:
        print("\n👋  Painel encerrado.")
