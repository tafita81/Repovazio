#!/usr/bin/env python3
"""
bannerbear_thumbnails.py — Gerar 5 thumbnails por video automaticamente
Acao 8: A/B test thumbnails via Bannerbear API → maior CTR

Cruzamento: Bannerbear + YouTube API + analytics
"""
import os, requests
BB_KEY = os.getenv("BANNERBEAR_API_KEY","")
TEMPLATES_THUMBNAIL = ["tmpl_narcisismo_1","tmpl_ansiedade_1","tmpl_geral_hook","tmpl_lista_7","tmpl_before_after"]
def gerar_thumbnail(titulo, template_id, variacao):
    if not BB_KEY: return {"url": "pendente_configurar_bannerbear"}
    r = requests.post("https://api.bannerbear.com/v2/images",
        headers={"Authorization": f"Bearer {BB_KEY}"},
        json={"template": template_id,
              "modifications": [{"name":"titulo","text":titulo},{"name":"variacao","text":variacao}]},
        timeout=30)
    return r.json() if r.status_code == 200 else {}
def run():
    print("ACAO 8: Bannerbear Thumbnail Generator")
    print("5 thumbnails por video, A/B test automatico")
    print("Config: bannerbear.com -> criar templates -> BANNERBEAR_API_KEY")
if __name__ == "__main__":
    run()
