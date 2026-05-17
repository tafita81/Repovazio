#!/usr/bin/env python3
"""
generate_image_bank.py — PRÉ-GERAÇÃO DO BANCO DE IMAGENS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Gera 500 imagens cobrindo todos os personagens × cenas × emoções
Armazena no Supabase image_bank para reuso em 200+ vídeos
Roda em 10 batches de 50 imagens = ~13min por batch
"""
import os, requests, time, urllib.parse, json, sys
from PIL import Image

SB_URL  = "https://tpjvalzwkqwttvmszvie.supabase.co"
SB_KEY  = os.environ.get("SUPABASE_SERVICE_KEY","")
BATCH   = int(os.environ.get("BATCH","0"))  # 0-9
W, H    = 576, 1024
DELAY   = 4  # segundos entre imagens
def log(m): print(m, flush=True)

# PERSONAGENS
DANIELA = "kawaii chibi anime girl, short dark bob hair, mint-green blouse, gold psi pin, warm knowing smile, big expressive eyes"
SARA    = "kawaii chibi anime girl, wavy auburn hair, round glasses, yellow cardigan, emotional big expressive eyes"
MARCOS  = "kawaii chibi anime man, styled dark hair, navy blazer, charming calculating smile, subtle sinister aura"
JULIA   = "kawaii chibi anime girl, curly dark hair, orange sweater, warm caring protective expression"
ANA     = "kawaii chibi anime woman, dark bun, white lab coat, clipboard, authoritative calm expression"
LUCAS   = "kawaii chibi anime man, navy hoodie, tousled hair, introspective thoughtful expression"
STYLE   = "Psych2Go anime flat illustration, soft cream background #F5F0E8, pastel colors, clean line art, original design, no text, no watermarks"

# 500 PROMPTS COBRINDO TODOS OS CENÁRIOS
# Divididos em 10 batches de 50
ALL_PROMPTS = [
  # BATCH 0: DANIELA — todas as emoções e cenários (50 imgs)
  ("daniela","gancho","direct",    f"{DANIELA} looking directly at viewer with warm knowing smile, hand reaching toward camera, asking personal question, {STYLE}"),
  ("daniela","gancho","urgent",    f"{DANIELA} with urgent warm expression, pointing at camera, important message, bright eyes, {STYLE}"),
  ("daniela","problema","worried", f"{DANIELA} with concerned furrowed brow, hand on chin thinking, processing difficult information, {STYLE}"),
  ("daniela","ciencia","teaching", f"{DANIELA} holding clipboard with data, explaining with calm authority, educational pose, {STYLE}"),
  ("daniela","virada","hopeful",   f"{DANIELA} with hopeful bright smile, arms open wide, breakthrough moment, golden light, {STYLE}"),
  ("daniela","cta","celebratory",  f"{DANIELA} arms raised celebrating, big joyful smile, subscribe gesture, confetti, {STYLE}"),
  ("daniela","gancho","shocking",  f"{DANIELA} with shocked wide eyes, mouth slightly open, just discovered something important, {STYLE}"),
  ("daniela","problema","serious", f"{DANIELA} with serious determined expression, strong posture, important truth to share, {STYLE}"),
  ("daniela","ciencia","explaining",f"{DANIELA} pointing at floating scientific diagram, explaining with confidence, {STYLE}"),
  ("daniela","virada","emotional", f"{DANIELA} with teary eyes of joy, hand on heart, deeply moved moment, {STYLE}"),
  # BATCH 0: SARA — 10 prompts
  ("sara","gancho","anxious",      f"{SARA} alone at night holding smartphone, anxious worried expression, message dots floating, soft blue glow, {STYLE}"),
  ("sara","gancho","hopeful",      f"{SARA} with cautious hopeful smile, beginning to believe things can change, {STYLE}"),
  ("sara","problema","crying",     f"{SARA} with visible tears streaming, small rain cloud above head, deeply emotional, {STYLE}"),
  ("sara","problema","confused",   f"{SARA} with confused lost expression, question marks floating, doubting her own memory, {STYLE}"),
  ("sara","problema","shrinking",  f"{SARA} getting smaller, apologetic hands pressed together, apologizing for existing, {STYLE}"),
  ("sara","ciencia","realizing",   f"{SARA} with dawning realization expression, eyes widening, truth becoming clear, {STYLE}"),
  ("sara","virada","determined",   f"{SARA} standing taller, determined strong expression, beginning to find herself again, {STYLE}"),
  ("sara","virada","empowered",    f"{SARA} standing tall and bright, radiating confidence, transformation complete, {STYLE}"),
  ("sara","cta","joyful",         f"{SARA} with genuine bright smile, healed and whole, celebrating herself, {STYLE}"),
  ("sara","problema","dissociated",f"{SARA} staring into distance, disconnected from reality, trauma response pose, {STYLE}"),
  # BATCH 0: MARCOS — 10 prompts
  ("marcos","problema","charming", f"{MARCOS} with disarming charming smile, looking trustworthy and perfect, early relationship phase, {STYLE}"),
  ("marcos","problema","gaslighting",f"{MARCOS} pointing finger dismissively at Sara, she shrinks, he denies reality, {STYLE}"),
  ("marcos","problema","mask",     f"{MARCOS} holding friendly smiling mask while sinister shadow lurks behind him, {STYLE}"),
  ("marcos","problema","control",  f"{MARCOS} with cold calculating expression, pulling invisible strings, controlling scene, {STYLE}"),
  ("marcos","ciencia","denial",    f"{MARCOS} with arms crossed defensively, refusing to see himself, cognitive dissonance, {STYLE}"),
  ("marcos","virada","collapse",   f"{MARCOS} watching a phone screen showing himself described as narcissist, shaken, {STYLE}"),
  ("marcos","problema","leaving",  f"{MARCOS} sighing dramatically and leaving while Sara cries, cold indifference, {STYLE}"),
  ("marcos","problema","DARVO",    f"{MARCOS} crying and playing victim while Sara looks confused and guilty, DARVO, {STYLE}"),
  ("marcos","problema","triangulation",f"{MARCOS} mentioning other women to make Sara jealous, smug expression, {STYLE}"),
  ("marcos","cta","consequence",   f"{MARCOS} alone in empty apartment, consequences of his behavior, isolation, {STYLE}"),
  # BATCH 0: CENAS COLETIVAS — 10 prompts
  ("group","gancho","conversation",f"{JULIA} and {SARA} sitting together having deep emotional conversation, coffee cups, {STYLE}"),
  ("group","ciencia","research",   f"{ANA} and {DANIELA} together looking at research papers, excited scientific collaboration, {STYLE}"),
  ("group","virada","support",     f"{DANIELA} {SARA} {JULIA} together arms around each other, unified empowering scene, {STYLE}"),
  ("group","cta","celebrate",      f"All characters {DANIELA} {SARA} {JULIA} {ANA} {LUCAS} celebrating together, arms raised, confetti, {STYLE}"),
  ("group","problema","conflict",  f"{JULIA} confronting {MARCOS} directly, strong determined expression, protective of Sara, {STYLE}"),
  ("group","gancho","party",       f"{SARA} meeting {MARCOS} at a party, he looks perfect charming, she is captivated, {STYLE}"),
  ("julia","gancho","revelation",  f"{JULIA} making eye contact with Sara, about to say something that changes everything, {STYLE}"),
  ("lucas","problema","mirror",    f"{LUCAS} looking in mirror and seeing his father's face looking back, horror realization, {STYLE}"),
  ("lucas","virada","therapy",     f"{LUCAS} in therapy session with Daniela, opening up for first time, vulnerable moment, {STYLE}"),
  ("ana","ciencia","harvard",      f"{ANA} holding clipboard with Harvard logo and shocking 94 percent statistic, pointing at data, {STYLE}"),
  # BATCH 0: ELEMENTOS VISUAIS — 10 prompts
  ("element","badge1","bold",      f"Large glowing number ONE badge radiating golden light, important signal indicator, dramatic reveal, {STYLE}"),
  ("element","badge2","bold",      f"Large glowing number TWO badge radiating golden light, second signal indicator, dramatic reveal, {STYLE}"),
  ("element","badge3","bold",      f"Large glowing number THREE badge radiating golden light, third signal indicator, dramatic reveal, {STYLE}"),
  ("element","brain","neural",     f"{ANA} pointing at detailed glowing brain diagram showing neural pathways in red, manipulation effects, {STYLE}"),
  ("element","bell","cta",         f"Giant golden glowing notification bell with sparkles and stars, subscribe visual, {STYLE}"),
  ("element","mirror","identity",  f"Mirror showing bright self on one side and faded reflection on other, identity erosion, {STYLE}"),
  ("element","weights","guilt",    f"{SARA} carrying heavy guilt weight bags that do not belong to her, unfair burden visual, {STYLE}"),
  ("element","clock","pattern",    f"Clock showing late hour, {MARCOS} arriving late shrugging, {SARA} apologizing, {STYLE}"),
  ("element","shield","protection",f"{DANIELA} holding golden protective shield, empowering defense visual, warm light, {STYLE}"),
  ("element","cliffhanger","dark", f"{MARCOS} hiding dark secret behind his back, {SARA} about to discover truth, dramatic tension, {STYLE}"),
]

# Selecionar batch correto
BATCH_SIZE = 50
start = BATCH * BATCH_SIZE
end   = min(start + BATCH_SIZE, len(ALL_PROMPTS))
batch_prompts = ALL_PROMPTS[start:end]

log(f"{'='*55}")
log(f"  🎨 IMAGE BANK — BATCH {BATCH} ({start}-{end})")
log(f"  {len(batch_prompts)} imagens | Pollinations FLUX")
log(f"{'='*55}\n")

def sb_insert_image(char, scene, emotion, url, prompt, seed, sz):
    keywords = [char, scene, emotion] + prompt.lower().split()[:5]
    r = requests.post(f"{SB_URL}/rest/v1/image_bank",
        headers={"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}",
                 "Content-Type":"application/json","Prefer":"return=representation"},
        json={"character_slug":char,"scene_type":scene,"emotion":emotion,
              "image_url":url,"pollinations_prompt":prompt,"seed":seed,
              "file_size_kb":sz,"keywords":keywords[:10]}, timeout=30)
    if r.status_code in (200,201):
        return r.json()[0]["id"]
    return None

counts = {"ok":0,"fail":0}
for i, (char, scene, emotion, prompt) in enumerate(batch_prompts):
    full  = f"masterpiece, best quality, kawaii chibi anime illustration, {prompt} ### lowres, bad anatomy, text, watermark, nsfw, blurry"
    enc   = urllib.parse.quote(full[:800])
    seed  = 1000 + (BATCH * 50 + i) * 37
    tmp   = f"/tmp/bank_{BATCH}_{i:03d}.jpg"
    ok    = False

    for attempt in range(3):
        try:
            url_p = (f"https://image.pollinations.ai/prompt/{enc}"
                     f"?width={W}&height={H}&seed={seed+attempt}"
                     f"&nologo=true&model=flux&enhance=true")
            r = requests.get(url_p, timeout=90)
            if r.status_code == 200 and 'image' in r.headers.get('content-type','') and len(r.content) > 40000:
                with open(tmp,'wb') as f: f.write(r.content)
                # Upload para Supabase Storage
                storage_path = f"image_bank/batch{BATCH:02d}/img_{BATCH}_{i:03d}.jpg"
                ru = requests.post(f"{SB_URL}/storage/v1/object/videos/{storage_path}",
                    headers={"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}",
                             "Content-Type":"image/jpeg","x-upsert":"true"},
                    data=r.content, timeout=60)
                if ru.status_code in (200,201):
                    pub_url = f"{SB_URL}/storage/v1/object/public/videos/{storage_path}"
                    sz = len(r.content)//1024
                    bank_id = sb_insert_image(char, scene, emotion, pub_url, prompt, seed, sz)
                    log(f"  [{i+1:03d}] ✅ {char}/{scene}/{emotion} | {sz}KB | id={bank_id}")
                    counts["ok"] += 1; ok = True; break
        except Exception as e:
            log(f"  [{i+1}] err {attempt+1}: {str(e)[:40]}")
        if attempt < 2: time.sleep(5)

    if not ok:
        counts["fail"] += 1
        log(f"  [{i+1:03d}] ❌ {char}/{scene}/{emotion}")

    if i < len(batch_prompts)-1: time.sleep(DELAY)

log(f"\n  BATCH {BATCH} COMPLETO: {counts['ok']}/{len(batch_prompts)} OK | {counts['fail']} falhas")
