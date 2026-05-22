#!/usr/bin/env python3
"""
b2b_licensing.py — Licenciar biblioteca de videos para B2B
Acao 11: Clinicas/hospitais/planos saude → R$500-2000/mes por licenca

Cruzamento: Hunter.io (encontrar emails) + Apollo.io + LLM (proposta)
"""
import os, requests
HUNTER_KEY = os.getenv("HUNTER_IO_KEY","")
GROQ_KEY = os.getenv("GROQ_API_KEY","")
PROSPECTS_TEMPLATE = ["clinica_psicologia","centro_saude_mental","hospital_psiquiatrico","plano_saude","rh_empresa_grande"]
def gerar_proposta_b2b(nome_empresa, segmento):
    if not GROQ_KEY: return ""
    r = requests.post("https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"},
        json={"model":"llama-3.3-70b-versatile",
              "messages":[{"role":"user","content":f"Escreva email proposta B2B para {nome_empresa} ({segmento}) para licenciar biblioteca de 100+ videos de psicologia para uso em clinica/empresa. Preco: R$500-2000/mes. Assinatura: Daniela Coelho. Tom: profissional, breve, focado em beneficio para pacientes."}],
              "max_tokens":400},
        timeout=30)
    if r.status_code == 200: return r.json()["choices"][0]["message"]["content"]
    return ""
def run():
    print("ACAO 11: B2B Licensing Engine")
    print("Target: clinicas, hospitais, planos saude, RH corporativo")
    print("Ticket: R$500-2000/mes | 10 clientes = R$5K-20K MRR")
    proposta = gerar_proposta_b2b("Instituto Saude Mental SP","clinica_psicologia")
    if proposta: print(f"\nExemplo proposta:\n{proposta[:300]}...")
if __name__ == "__main__":
    run()
