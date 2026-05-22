#!/usr/bin/env python3
"""
multi_canal_setup.py — Configurar 4 canais satelite com mesmo pipeline
Acao 10: TDAH + Ansiedade + Relacionamentos + EN Psychology

Cruzamento: YouTube Data API + pipeline existente × 4
RPM total esperado: 4-5x canal atual
"""
import os, json
CANAIS = [
    {"nome":"TDAH Adulto BR","nicho":"tdah","idioma":"PT-BR","rpms_esperado":2.5,"keywords":["tdah adulto","deficit atencao","impulsividade"]},
    {"nome":"Ansiedade e Panico BR","nicho":"ansiedade","idioma":"PT-BR","rpms_esperado":2.8,"keywords":["ansiedade","ataque panico","fobia social"]},
    {"nome":"Relacionamentos Conscientes BR","nicho":"relacionamentos","idioma":"PT-BR","rpms_esperado":3.0,"keywords":["relacionamento toxico","apego","limites"]},
    {"nome":"Psychology Insights EN","nicho":"psychology","idioma":"EN","rpms_esperado":8.5,"keywords":["narcissism","anxiety","mental health"]},
]
def run():
    print("ACAO 10: Multi-Canal Setup")
    for c in CANAIS:
        print(f"  {c['nome']}: {c['idioma']} | RPM ${c['rpms_esperado']}")
    print("\n  Para criar: studio.youtube.com -> Switch account -> Create channel")
    print("  Mesmo pipeline gera conteudo para TODOS os canais")
    total_rpm = sum(c["rpms_esperado"] for c in CANAIS)
    print(f"  RPM combinado: ~${total_rpm:.1f} por 1000 views totais")
if __name__ == "__main__":
    run()
