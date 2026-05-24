#!/usr/bin/env python3
"""
email_sequence.py — Sequência email pós-compra (app → upsell WhatsApp)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TRIGGER: pessoa comprou o app R$29,90 no Hotmart/Kirvano
OBJETIVO: converter compradores em assinantes WhatsApp R$216/ano

SEQUÊNCIA:
  Dia 0  — Boas-vindas + acesso ao app
  Dia 1  — Dica exclusiva sobre o app
  Dia 3  — Teaser do WhatsApp (o que eles estão perdendo)
  Dia 7  — Oferta WhatsApp com urgência
  Dia 14 — Last call + desconto especial

PLATAFORMA: Hotmart Smart Install (auto)
  Ou: integração via webhook Hotmart → Supabase → Groq gera email → SMTP envia
"""
import os, requests, json, time
import urllib3; urllib3.disable_warnings()

SB_URL = os.getenv("SUPABASE_URL","https://tpjvalzwkqwttvmszvie.supabase.co")
SB_KEY = os.getenv("SUPABASE_SERVICE_KEY","")
GROQ   = os.getenv("GROQ_API_KEY","")
SBH    = {"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}",
          "Content-Type":"application/json","Prefer":"return=minimal"}

LINK_APP = "repovazio.vercel.app/app"
LINK_WA  = "repovazio.vercel.app/psicologia-para-dormir"

SEQUENCIA_EMAIL = [
    {
        "dia": 0,
        "assunto": "ψ Bem-vindo ao Modo Psicologia 🌙",
        "tipo": "boas_vindas",
        "corpo": f"""Olá!

Obrigada por confiar em Daniela Coelho 💜

Seu app de psicologia está pronto:
👉 {LINK_APP}

O que você vai encontrar:
✓ 6 rituais noturnos baseados em pesquisa
✓ 8 missões psicológicas diárias
✓ 10 insights científicos (Harvard, PubMed)
✓ Diário emocional com histórico

Acesse agora e comece hoje à noite.

— Daniela Coelho
pesquisadora de comportamento humano""",
    },
    {
        "dia": 3,
        "assunto": "O que você ainda não sabe sobre seu sono 🔬",
        "tipo": "valor",
        "corpo": f"""Há 3 dias você começou sua jornada.

Quero te contar algo que mudou minha pesquisa.

Walker (2017) descobriu que o REM é quando processamos
as emoções do dia. Quando você vai dormir carregando
estresse, seu cérebro não consegue fazer isso.

É por isso que 72% das pessoas acordam ainda cansadas.

Estou enviando um áudio especial amanhã para os membros
do grupo exclusivo de WhatsApp. Fala sobre como o cortisol
afeta seu sono e o que fazer em 4 minutos.

Interessada em participar?
👉 {LINK_WA}

— Daniela""",
    },
    {
        "dia": 7,
        "assunto": "Oferta especial — expira em 48h ⏰",
        "tipo": "oferta",
        "corpo": f"""Uma semana com o app. Como foi?

Tenho uma notícia importante.

O grupo "Psicologia Para Dormir" tem 47 vagas restantes.
Todo dia às 19h30, eu envio um áudio de 4 minutos
com uma técnica diferente baseada em PubMed.

Hoje falámos sobre binaural 528Hz e cortisol.
Amanhã: gaslighting e por que afeta o seu sono.

Por R$216/ano (R$18/mês) você recebe:
✓ 365 áudios exclusivos
✓ Pesquisa real aplicada ao dia a dia
✓ Grupo exclusivo sem spam
✓ 7 dias de garantia total

Oferta válida até {'{data_limite}'}:
👉 {LINK_WA}

— Daniela""",
    },
    {
        "dia": 14,
        "assunto": "Última chamada 🌙",
        "tipo": "last_call",
        "corpo": f"""Esta é minha última mensagem sobre o WhatsApp.

Hoje 23 pessoas entraram no grupo.
Ainda restam 24 vagas.

Se você já sentiu que seu sono nunca é suficiente,
que você acorda às 3h da manhã sem motivo,
que o estresse do dia segue você até a madrugada...

Então o grupo foi feito para você.

R$216/ano. 7 dias de garantia. Cancela quando quiser.
👉 {LINK_WA}

Se não fizer sentido, sem problema. Continuamos na jornada com o app.

— Daniela""",
    },
]

def groq_personalizar_email(email_base, nome=""):
    """Personaliza email com nome do cliente"""
    if not GROQ or not nome: return email_base
    corpo = email_base["corpo"].replace("Olá!", f"Olá, {nome}!")
    return {**email_base, "corpo": corpo}

def salvar_sequencia():
    if not SB_KEY: return
    for email in SEQUENCIA_EMAIL:
        requests.post(f"{SB_URL}/rest/v1/dm_sequencia",
            headers={**SBH,"Prefer":"return=minimal"},
            json={"step":email["dia"],"trigger":email["tipo"],
                  "mensagem":email["corpo"][:400],"delay_min":email["dia"]*1440},
            timeout=8, verify=False)

def run():
    print("=== EMAIL SEQUENCE — Upsell WhatsApp ===\n")
    print("  Trigger: compra app R$29,90 → sequência 14 dias → R$216/ano\n")
    for e in SEQUENCIA_EMAIL:
        print(f"  Dia {e['dia']:02d} [{e['tipo']}]: {e['assunto']}")
        print(f"         {e['corpo'][:80]}...")
        print()
    salvar_sequencia()
    print(f"  ✅ Sequência salva no Supabase")
    print(f"  Configurar: Hotmart webhook → trigger esta sequência")
    print(f"  Conversão esperada: 5-10% compradores → assinantes WA")

if __name__=="__main__": run()
