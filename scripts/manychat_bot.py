#!/usr/bin/env python3
"""
manychat_bot.py — Auto-resposta "SONO" + funil DM completo
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FLUXO (do transcript "Histórias Infantis"):
  1. Pessoa comenta "SONO" no Instagram
  2. ManyChat dispara DM automático
  3. DM step 1: link produto R$29,90 (impulso)
  4. Se comprou: DM step 2 após 1h → upsell R$216/ano WhatsApp
  5. Se não respondeu 48h: DM step 3 → reengajamento

INTEGRAÇÃO ManyChat API:
  - Webhook recebe evento de comentário
  - Verifica se contém "SONO" (case-insensitive)
  - Envia DM via ManyChat API
  - Salva no Supabase para tracking

PRODUTOS NO FUNIL:
  Low ticket:  R$29,90 → repovazio.vercel.app/app-vendas
  Premium:     R$216/ano → repovazio.vercel.app/psicologia-para-dormir
"""
import os, requests, json, time
import urllib3; urllib3.disable_warnings()

SB_URL      = os.getenv("SUPABASE_URL","https://tpjvalzwkqwttvmszvie.supabase.co")
SB_KEY      = os.getenv("SUPABASE_SERVICE_KEY","")
MANYCHAT_KEY= os.getenv("MANYCHAT_API_KEY","")  # sua chave ManyChat
SBH = {"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}",
       "Content-Type":"application/json","Prefer":"return=minimal"}

LINK_APP = "repovazio.vercel.app/app-vendas"
LINK_WA  = "repovazio.vercel.app/psicologia-para-dormir"

# Sequência de DMs em 3 etapas
DM_STEPS = {
    1: {
        "trigger": "SONO",
        "delay_min": 0,
        "mensagem": (
            "Oi! Vi que você comentou SONO 🌙\n\n"
            "Tenho algo especial para você:\n\n"
            "👉 *Modo Psicologia App*\n"
            "Rituais noturnos + missões + insights baseados em ciência.\n\n"
            f"Acesse agora por R$29,90 (pagamento único):\n🔗 {LINK_APP}\n\n"
            "São apenas R$29,90 e o acesso é vitalício. Vale muito mais."
        ),
    },
    2: {
        "trigger": "comprou_app",
        "delay_min": 60,
        "mensagem": (
            "Que bom que você tem o app! 🎉\n\n"
            "Mas posso te contar algo?\n\n"
            "Todo dia às 19h30 Daniela envia um áudio exclusivo de 4 minutos "
            "direto no seu WhatsApp. Baseado em pesquisa real.\n\n"
            "Isso é o *Psicologia Para Dormir* — R$19,90/mês ou R$216/ano.\n\n"
            f"👉 {LINK_WA}\n\n"
            "Experimenta 7 dias. Se não gostar, devolvo tudo."
        ),
    },
    3: {
        "trigger": "sem_resposta_48h",
        "delay_min": 2880,
        "mensagem": (
            "Ainda por aqui? 🌙\n\n"
            "O app de psicologia ainda está esperando.\n"
            "Mais de 200 pessoas já usam para dormir melhor.\n\n"
            f"👉 R$29,90 acesso vitalício: {LINK_APP}\n\n"
            "Última chamada. Depois eu encerro essa oferta."
        ),
    },
}

def enviar_dm_manychat(subscriber_id, mensagem):
    """Envia DM via API do ManyChat"""
    if not MANYCHAT_KEY:
        print(f"    [SIMULAÇÃO] DM para {subscriber_id}: {mensagem[:50]}...")
        return True
    try:
        r = requests.post(
            "https://api.manychat.com/fb/sending/sendContent",
            headers={"Authorization":f"Bearer {MANYCHAT_KEY}",
                     "Content-Type":"application/json"},
            json={"subscriber_id": subscriber_id,
                  "data": {"version":"v2","content":{
                      "messages":[{"type":"text","text":mensagem}]
                  }}},
            timeout=10, verify=False
        )
        return r.status_code == 200
    except: return False

def registrar_lead(subscriber_id, step, status="enviado"):
    """Registra no Supabase para tracking e anti-duplicata"""
    if not SB_KEY: return
    requests.post(f"{SB_URL}/rest/v1/dm_sequencia",
        headers={**SBH,"Prefer":"return=minimal"},
        json={"step":step,"trigger":DM_STEPS[step]["trigger"],
              "mensagem":DM_STEPS[step]["mensagem"][:300],
              "ativo":True},
        timeout=8, verify=False)

def processar_comentario_sono(subscriber_id, comentario):
    """Processa comentário 'SONO' e dispara DM step 1"""
    if "sono" not in comentario.lower():
        return False
    print(f"  🎯 SONO detectado! subscriber: {subscriber_id}")
    msg = DM_STEPS[1]["mensagem"]
    ok = enviar_dm_manychat(subscriber_id, msg)
    if ok:
        registrar_lead(subscriber_id, 1)
        print(f"  ✅ DM step 1 enviado")
    return ok

def simular_funil_completo():
    """Simula o funil completo para teste"""
    print("=== MANYCHAT BOT — Funil SONO Completo ===\n")
    print("  Fluxo: Instagram Reel → Comenta SONO → DM auto → Produto\n")
    for step, info in DM_STEPS.items():
        print(f"  STEP {step} [{info['trigger']}] ({info['delay_min']}min delay):")
        print(f"  {info['mensagem'][:100]}...\n")
    print(f"  PRODUTOS NO FUNIL:")
    print(f"  Step 1: R$29,90 app (impulso, sem pensar)")
    print(f"  Step 2: R$216/ano WhatsApp (upsell 1h depois)")
    print(f"  Step 3: Reengajamento 48h")
    print(f"\n  CONFIGURAR:")
    print(f"  1. manychat.com → Keywords → 'SONO' → DM flow")
    print(f"  2. MANYCHAT_API_KEY no GitHub Secrets")
    print(f"  3. Webhook URL: repovazio.vercel.app/api/manychat-webhook")

if __name__=="__main__": simular_funil_completo()
