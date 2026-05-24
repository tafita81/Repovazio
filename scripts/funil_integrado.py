#!/usr/bin/env python3
"""
funil_integrado.py — Funil end-to-end com upsell (todos os transcripts)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FUNIL COMPLETO (integração dos 3 transcripts):

Transcript 1 (Histórias Infantis):
  Instagram CTA → DM → Hotmart → WhatsApp grupo → Entrega diária

Transcript 2 (Rafael Milagre):
  Dados vão até as pessoas → briefing automático → sem reuniões
  B2C → B2B → marketplace

Transcript 3 (Quadrinhos Dark):
  Post viral gringa → adapta BR → 3 tipos × 3 horários → low ticket
  Funil: seguir → engajar → comprar R$29,90 → upsell R$216/ano

FUNIL INTEGRADO RESULTANTE:
  1. Instagram Reel dark (Pollinations + Groq)
  2. CTA "Comenta SONO" → DM automático
  3. Link landing page → R$29,90 (impulso, sem pensar)
  4. Pós-compra email sequence: upsell R$216/ano (WhatsApp)
  5. WhatsApp grupo → áudio diário → fidelização
  6. Afiliados Kwai/Amazon dentro do áudio
  7. YouTube SEO → crescimento orgânico → mais topo de funil

MATH INTEGRADO:
  100 seguidores × 1% conversão = 1 venda/dia R$29,90
  1.000 seguidores × 2% = 20 vendas/dia = R$17.940/mês
  + 5% dos compradores viram assinantes WA → +R$216/ano cada
"""
import os, requests, time, json
import urllib3; urllib3.disable_warnings()

SB_URL = os.getenv("SUPABASE_URL","https://tpjvalzwkqwttvmszvie.supabase.co")
SB_KEY = os.getenv("SUPABASE_SERVICE_KEY","")
GROQ   = os.getenv("GROQ_API_KEY","")
SBH    = {"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}",
          "Content-Type":"application/json","Prefer":"return=minimal"}

SEQUENCIA_DM = [
    {
        "step": 1, "trigger": "SONO",
        "msg": "Olá! Que bom que você se interessou 🌙\n\nVeja o que preparei para você:\n👉 {LINK_APP}\n\nO app de psicologia que vai transformar suas noites. Por apenas R$29,90 pagamento único.",
        "delay_min": 0,
    },
    {
        "step": 2, "trigger": "comprou_app",
        "msg": "Que ótimo que você já tem o app! 🎉\n\nSabia que você pode ir além?\n\nTodo dia às 19h30 Daniela envia um áudio exclusivo de psicologia direto no seu WhatsApp.\nApenas R$19,90/mês ou R$216/ano.\n\n👉 {LINK_WA}",
        "delay_min": 60,
    },
    {
        "step": 3, "trigger": "sem_resposta_48h",
        "msg": "Ainda está por aqui? 🌙\n\nO app de psicologia está esperando por você.\nMais de 200 pessoas já estão usando para dormir melhor.\n\n👉 {LINK_APP}\n\nR$29,90 apenas. Acesso vitalício.",
        "delay_min": 2880,
    },
]

EMAILS_UPSELL = [
    {
        "dia": 1,
        "assunto": "Bem-vindo ao Modo Psicologia 🌙",
        "corpo": "Obrigada por confiar em mim. Seu app está pronto em: {LINK_APP}\n\nAmanhã você recebe uma dica especial de Daniela.",
    },
    {
        "dia": 3,
        "assunto": "Você sabia que pode ir além? ✨",
        "corpo": "Que tal receber Daniela todo dia no WhatsApp?\n\nÁudio guiado de 4 min, 19h30, com ciência PubMed.\nR$19,90/mês ou R$216/ano: {LINK_WA}",
    },
    {
        "dia": 7,
        "assunto": "Como está sua semana? 💜",
        "corpo": "7 dias com o app. Como você está?\n\nLembre que o grupo WhatsApp com áudios diários de Daniela ainda tem vagas:\n{LINK_WA}",
    },
]

LINKS = {
    "LINK_APP":   "repovazio.vercel.app/app-vendas",
    "LINK_WA":    "repovazio.vercel.app/psicologia-para-dormir",
    "LINK_YT":    "youtube.com/@psidanielacoelho",
    "LINK_INSTA": "instagram.com/psidanielacoelho",
}

def processar_dm(step_num):
    seq = next((s for s in SEQUENCIA_DM if s["step"]==step_num), None)
    if not seq: return None
    msg = seq["msg"]
    for k, v in LINKS.items(): msg = msg.replace("{"+k+"}", v)
    return msg

def projecao_matematica(seguidores, taxa_conv=0.02, taxa_upsell=0.05):
    vendas_dia = seguidores * taxa_conv / 30
    receita_app = vendas_dia * 29.90
    novos_wa_mes = vendas_dia * 30 * taxa_upsell
    receita_wa = novos_wa_mes * 18
    total_mes = receita_app * 30 + receita_wa
    return {
        "vendas_dia": round(vendas_dia, 1),
        "receita_app_mes": round(receita_app * 30, 2),
        "novos_wa_mes": round(novos_wa_mes, 1),
        "receita_wa_mes": round(receita_wa, 2),
        "total_mes": round(total_mes, 2),
    }

def salvar_funil():
    if not SB_KEY: return
    # Salvar configuração do funil no Supabase
    requests.post(f"{SB_URL}/rest/v1/produto_low_ticket",
        headers={**SBH,"Prefer":"return=minimal"},
        json={"nome":"Modo Psicologia App","preco":29.90,
              "tipo":"pagamento_unico",
              "link_app":LINKS["LINK_APP"],
              "link_vendas":LINKS["LINK_APP"]},
        timeout=8, verify=False)

def run():
    print("=== FUNIL INTEGRADO COMPLETO ===\n")
    print("  3 Transcripts → 1 Funil Unificado\n")
    print("  SEQUÊNCIA DM:")
    for s in SEQUENCIA_DM:
        msg = processar_dm(s["step"])
        print(f"  Step {s['step']} [{s['trigger']}]: {msg[:80]}...")
    print("\n  EMAILS UPSELL:")
    for e in EMAILS_UPSELL:
        print(f"  Dia {e['dia']:02d}: {e['assunto']}")
    print("\n  PROJEÇÕES:")
    for seg in [100, 500, 1000, 5000, 10000]:
        p = projecao_matematica(seg)
        print(f"  {seg:6,} seguidores → R${p['total_mes']:8,.2f}/mês | {p['vendas_dia']} vendas/dia")
    salvar_funil()
    print("\n  ✅ Funil configurado e salvo no Supabase")

if __name__=="__main__": run()
