#!/usr/bin/env python3
"""
smolagents_orchestrator.py — Agente autonomo HuggingFace SmolAgents
Acao 15-20: Orquestra todo o pipeline automaticamente

Cruzamento: SmolAgents (HF no-auth) + todos os outros scripts
O agente decide o que fazer, quando fazer, em qual idioma
"""
import os, subprocess, json
from datetime import datetime

PIPELINE_TOOLS = [
    {"nome": "youtube_growth_engine", "frequencia": "diaria", "script": "scripts/youtube_growth_engine.py"},
    {"nome": "affiliate_ugc_engine", "frequencia": "2x_dia", "script": "scripts/affiliate_ugc_engine.py"},
    {"nome": "research_monitor", "frequencia": "diaria", "script": "scripts/research_monitor.py"},
    {"nome": "quote_pod_engine", "frequencia": "noturno", "script": "scripts/quote_pod_engine.py"},
    {"nome": "en_channel_engine", "frequencia": "por_video", "script": "scripts/en_channel_engine.py"},
    {"nome": "trend_surfer", "frequencia": "2h", "script": "scripts/trend_surfer.py"},
    {"nome": "reddit_video_engine", "frequencia": "diaria", "script": "scripts/reddit_video_engine.py"},
    {"nome": "newsletter_engine", "frequencia": "semanal", "script": "scripts/newsletter_engine.py"},
    {"nome": "kdp_multilingual", "frequencia": "semanal", "script": "scripts/kdp_multilingual.py"},
    {"nome": "redbubble_batch", "frequencia": "noturno", "script": "scripts/redbubble_batch_engine.py"},
]

def status_do_sistema():
    print("=== QUANTUM BRAIN STATUS ===")
    print(f"Pipeline tools ativos: {len(PIPELINE_TOOLS)}")
    print(f"Ultima execucao: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    for t in PIPELINE_TOOLS:
        print(f"  [{t['frequencia']:12s}] {t['nome']}")
    print()
    print("GitHub Actions ativas:")
    actions = ["brain-auto-expand","affiliate-ugc-engine","research-monitor",
               "quote-pod-engine","en-channel-engine"]
    for a in actions:
        print(f"  • {a}.yml")

def run():
    status_do_sistema()
    print()
    print("SmolAgents orquestrador: awaiting HF key para ativacao total")
    print("Ate la: todas as acoes rodam via GitHub Actions schedule")

if __name__ == "__main__":
    run()
