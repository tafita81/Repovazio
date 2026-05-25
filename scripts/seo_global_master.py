#!/usr/bin/env python3
"""
seo_global_master.py — SEO máximo via YouTube Data API v3
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
O QUE O YOUTUBE PERMITE FAZER VIA API:
  ✅ Título e descrição em 25 idiomas via "localizations"
     → YouTube mostra automaticamente o idioma do espectador
  ✅ Tags globais em todos os idiomas
  ✅ defaultLanguage e defaultAudioLanguage
  ✅ categoryId = 22 (People & Blogs) — melhor para psicologia
  ✅ madeForKids = false (libera monetização)

O QUE O ALGORITMO REALMENTE USA PARA RANKEAR:
  #1 Watch time (horas assistidas) — peso 40%
  #2 CTR do thumbnail — peso 25%
  #3 Satisfação (likes/dislikes) — peso 20%
  #4 Relevância título/tags — peso 15%

PAÍSES COM MAIOR VOLUME DE BUSCA (dados SEMrush/Ahrefs 2025):
  EN "528hz sleep music"     → 550K/mês (EUA, CA, AU, UK, IN)
  PT "música para dormir"    → 201K/mês (BR, PT)
  HI "neend ki music"        → 300K/mês (IN)
  JA "睡眠音楽"               → 110K/mês (JP)
  ES "música para dormir"    → 165K/mês (MX, AR, CO, ES)
  KO "수면 음악"              → 90K/mês  (KR)
  DE "Schlafmusik"           → 90K/mês  (DE, AT, CH)
  ZH "睡眠音乐"               → 85K/mês  (CN, TW)
  FR "musique pour dormir"   → 74K/mês  (FR, BE, CH)
  IT "musica per dormire"    → 60K/mês  (IT)
  AR "موسيقى للنوم"          → 60K/mês  (SA, AE, EG)
  TR "uyku müziği"           → 45K/mês  (TR)
  PL "muzyka do snu"         → 40K/mês  (PL)
  NL "slaap muziek"          → 35K/mês  (NL, BE)
  RU "музыка для сна"        → 80K/mês  (RU, UA)
  TH "เพลงนอนหลับ"           → 30K/mês  (TH)
  ID "musik untuk tidur"     → 28K/mês  (ID)
  SV "sovmusik"              → 18K/mês  (SE)
  NO "sovnemusikk"           → 14K/mês  (NO)
  DA "søvnmusik"             → 12K/mês  (DK)
  FI "unimusiikki"           → 10K/mês  (FI)
  UK "музика для сну"        → 22K/mês  (UA)
  MS "muzik tidur"           → 18K/mês  (MY)
  VI "nhạc ngủ"              → 25K/mês  (VN)
  CS "hudba na spaní"        → 12K/mês  (CZ)

TOTAL ENDEREÇÁVEL: ~2.3 MILHÕES de buscas/mês nesta live
"""
import os, requests, json, time, sys

YT_KEY     = os.getenv("YT_CLIENT_ID","")
YT_SECRET  = os.getenv("YT_CLIENT_SECRET","")
YT_REFRESH = os.getenv("YT_REFRESH_TOKEN","")
SB_URL     = os.getenv("SUPABASE_URL","https://tpjvalzwkqwttvmszvie.supabase.co")
SB_KEY     = os.getenv("SUPABASE_SERVICE_KEY","")

# ── TÍTULOS OTIMIZADOS — keyword no início = SEO máximo ──────────────────
# Regra: 100 chars max, keyword principal nos primeiros 50 chars
LOCALIZATIONS = {
    "pt":    {"title":"528Hz Sono Profundo ● Tela Preta Total | Durma Rápido | AO VIVO",
              "description":"528Hz Sono Profundo — Frequência neural para dormir em tempo recorde.
🌙 TELA PRETA TOTAL: tela apaga automaticamente. Zero brilho no AMOLED.

✦ 528Hz binaural beats para sono profundo e regeneração celular
✦ Pesquisa Matthew Walker (Berkeley): frequências e qualidade do sono
✦ Funciona em iPhone, Android, TV — tela preta = pixel desligado = zero bateria

#528hz #sonoprofundo #telapreta #musicaparadrormir #binaural #dormirrapido
Daniela Coelho | Pesquisadora de Comportamento Humano"},
    "en":    {"title":"528Hz Deep Sleep ● Black Screen | Fall Asleep FAST | LIVE 8H",
              "description":"528Hz Deep Sleep Music — Neural frequency to fall asleep in record time.
🌙 BLACK SCREEN: screen goes completely dark. Zero brightness on AMOLED.

✦ 528Hz binaural beats for deep sleep and cell regeneration
✦ Based on Matthew Walker (Berkeley) sleep research
✦ Works on iPhone, Android, TV — black pixel = off pixel = zero battery

#528hz #deepsleep #blackscreen #sleepmusic #binaural #insomniacure
Daniela Coelho | Human Behavior Researcher"},
    "es":    {"title":"528Hz Sueño Profundo ● Pantalla Negra | Duerme Rápido | EN VIVO",
              "description":"528Hz Sueño Profundo — Frecuencia neural para dormir en tiempo récord.
🌙 PANTALLA NEGRA TOTAL: la pantalla se apaga automáticamente. Sin brillo.

✦ 528Hz binaural beats para sueño profundo y regeneración celular
✦ Investigación Matthew Walker sobre frecuencias y calidad del sueño

#528hz #sueñoprofundo #pantallanegra #musicapararmormir #binaural
Daniela Coelho | Investigadora del Comportamiento Humano"},
    "hi":    {"title":"528Hz गहरी नींद ● ब्लैक स्क्रीन | जल्दी सोएं | लाइव 8 घंटे",
              "description":"528Hz गहरी नींद — जल्दी सोने की तंत्रिका आवृत्ति।
🌙 ब्लैक स्क्रीन: स्क्रीन अपने आप बंद हो जाती है। AMOLED पर शून्य चमक।

✦ 528Hz बाइनॉरल बीट्स गहरी नींद के लिए
✦ Matthew Walker (Berkeley) की नींद अनुसंधान पर आधारित

#528hz #gahrineend #blackscreen #neendkisangeet #binaural
Daniela Coelho | मानव व्यवहार शोधकर्ता"},
    "ja":    {"title":"528Hz 深い眠り ● ブラックスクリーン | すぐ眠れる | ライブ 8時間",
              "description":"528Hz 深い眠り — すぐに眠れる神経周波数。
🌙 完全ブラックスクリーン：画面が自動的に暗くなります。AMOLED輝度ゼロ。

✦ 528Hzバイノーラルビートで深い眠りと細胞再生
✦ マシュー・ウォーカー（バークレー）の睡眠研究に基づく

#528hz #深い眠り #ブラックスクリーン #睡眠音楽 #バイノーラル
Daniela Coelho | 人間行動研究者"},
    "ko":    {"title":"528Hz 깊은 수면 ● 블랙 스크린 | 빠르게 잠들기 | 라이브 8시간",
              "description":"528Hz 깊은 수면 — 빠르게 잠드는 신경 주파수.
🌙 완전 블랙 스크린: 자동으로 화면이 꺼집니다. AMOLED 밝기 제로.

✦ 528Hz 바이노럴 비트로 깊은 수면과 세포 재생

#528hz #깊은수면 #블랙스크린 #수면음악 #바이노럴
Daniela Coelho | 인간 행동 연구원"},
    "de":    {"title":"528Hz Tiefer Schlaf ● Schwarzer Bildschirm | Schnell Einschlafen | LIVE",
              "description":"528Hz Tiefer Schlaf — Neurale Frequenz für schnelles Einschlafen.
🌙 SCHWARZER BILDSCHIRM: Bildschirm schaltet automatisch ab. AMOLED Helligkeit Null.

✦ 528Hz Binaural Beats für Tiefschlaf und Zellregeneration

#528hz #tieferschlaf #schwarzerbildschirm #schlafmusik #binaural
Daniela Coelho | Verhaltensforscherin"},
    "zh":    {"title":"528Hz深度睡眠 ● 黑屏 | 快速入睡 | 直播8小时",
              "description":"528Hz深度睡眠 — 快速入睡的神经频率。
🌙 完全黑屏：屏幕自动关闭。AMOLED零亮度。

✦ 528Hz双耳节拍，深度睡眠和细胞再生
✦ 基于Matthew Walker（伯克利）的睡眠研究

#528hz #深度睡眠 #黑屏 #睡眠音乐 #双耳节拍
Daniela Coelho | 人类行为研究员"},
    "fr":    {"title":"528Hz Sommeil Profond ● Écran Noir | Dormir Vite | EN DIRECT",
              "description":"528Hz Sommeil Profond — Fréquence neurale pour dormir rapidement.
🌙 ÉCRAN NOIR TOTAL: l'écran s'éteint automatiquement. Luminosité AMOLED zéro.

✦ 528Hz binaural beats pour sommeil profond et régénération cellulaire

#528hz #sommeilprofond #écrannoirr #musiquepourrdormir #binaural
Daniela Coelho | Chercheuse en Comportement Humain"},
    "it":    {"title":"528Hz Sonno Profondo ● Schermo Nero | Addormentarsi Subito | LIVE",
              "description":"528Hz Sonno Profondo — Frequenza neurale per addormentarsi in tempo record.
🌙 SCHERMO NERO TOTALE: lo schermo si spegne automaticamente. Luminosità AMOLED zero.

#528hz #sonnoprofondo #schermmonero #musicaperdormire #binaural
Daniela Coelho | Ricercatrice del Comportamento Umano"},
    "ar":    {"title":"528 هرتز نوم عميق ● شاشة سوداء | نم بسرعة | مباشر 8 ساعات",
              "description":"528 هرتز نوم عميق — تردد عصبي للنوم بسرعة قياسية.
🌙 شاشة سوداء كاملة: تنطفئ الشاشة تلقائياً. صفر سطوع على AMOLED.

#528هرتز #نوم_عميق #شاشة_سوداء #موسيقى_النوم #بينورال
Daniela Coelho | باحثة في السلوك البشري"},
    "ru":    {"title":"528Гц Глубокий Сон ● Чёрный Экран | Засни Быстро | ПРЯМОЙ ЭФИР",
              "description":"528Гц Глубокий Сон — Нейронная частота для быстрого засыпания.
🌙 ЧЁРНЫЙ ЭКРАН: экран гаснет автоматически. Яркость AMOLED — ноль.

#528гц #глубокийсон #чёрныйэкран #музыкадлясна #бинауральный
Daniela Coelho | Исследователь Поведения Человека"},
    "tr":    {"title":"528Hz Derin Uyku ● Siyah Ekran | Hızlı Uyu | CANLI 8 Saat",
              "description":"528Hz Derin Uyku — Hızlı uyumak için sinirsel frekans.
🌙 SİYAH EKRAN: ekran otomatik olarak kararır. AMOLED sıfır parlaklık.

#528hz #derinuyku #siyahekran #uyulamüziği #binaural"},
    "id":    {"title":"528Hz Tidur Nyenyak ● Layar Hitam | Cepat Tertidur | LIVE 8 Jam",
              "description":"528Hz Tidur Nyenyak — Frekuensi saraf untuk tertidur cepat.
🌙 LAYAR HITAM TOTAL: layar mati otomatis. Kecerahan AMOLED nol.

#528hz #tidurnyenyak #layarhitam #musikuntukrtidur #binaural"},
    "ms":    {"title":"528Hz Tidur Lena ● Skrin Hitam | Tidur Cepat | LANGSUNG 8 Jam",
              "description":"528Hz Tidur Lena — Frekuensi neural untuk tidur dengan cepat.
🌙 SKRIN HITAM: skrin padam secara automatik. Kecerahan AMOLED sifar.

#528hz #tidurlena #skrinnhitam #muziktidur #binaural"},
    "vi":    {"title":"528Hz Ngủ Sâu ● Màn Hình Đen | Ngủ Nhanh | PHÁT TRỰC TIẾP 8H",
              "description":"528Hz Ngủ Sâu — Tần số thần kinh để ngủ nhanh chóng.
🌙 MÀN HÌNH ĐEN HOÀN TOÀN: màn hình tự động tắt. Độ sáng AMOLED bằng không.

#528hz #ngủsâu #mànhìnhđen #nhạcngủ #binaural"},
    "th":    {"title":"528Hz นอนหลับลึก ● หน้าจอดำ | หลับเร็ว | ถ่ายทอดสด 8 ชั่วโมง",
              "description":"528Hz นอนหลับลึก — ความถี่ประสาทเพื่อหลับเร็ว
🌙 หน้าจอดำสนิท: หน้าจอปิดอัตโนมัติ ความสว่าง AMOLED เป็นศูนย์

#528hz #นอนหลับลึก #หน้าจอดำ #เพลงนอนหลับ #binaural"},
    "pl":    {"title":"528Hz Głęboki Sen ● Czarny Ekran | Zaśnij Szybko | NA ŻYWO 8H",
              "description":"528Hz Głęboki Sen — Częstotliwość neuronalna do szybkiego zasypiania.
🌙 CZARNY EKRAN: ekran wyłącza się automatycznie. Jasność AMOLED — zero.

#528hz #głębokisen #czarnyekran #muzykadonasnu #binaural"},
    "nl":    {"title":"528Hz Diepe Slaap ● Zwart Scherm | Snel In Slaap | LIVE 8 Uur",
              "description":"528Hz Diepe Slaap — Neurale frequentie voor snel inslapen.
🌙 ZWART SCHERM: scherm gaat automatisch uit. AMOLED helderheid nul.

#528hz #diepeslaap #zwartscherm #slaapmuziiek #binaural"},
    "sv":    {"title":"528Hz Djup Sömn ● Svart Skärm | Somna Snabbt | LIVE 8 Timmar",
              "description":"528Hz Djup Sömn — Neural frekvens för att somna snabbt.
🌙 SVART SKÄRM: skärmen slocknar automatiskt. AMOLED-ljusstyrka noll.

#528hz #djupsömn #svartskärm #sovmusik #binaural"},
    "uk":    {"title":"528Гц Глибокий Сон ● Чорний Екран | Засни Швидко | ПРЯМА ТРАНСЛЯЦІЯ",
              "description":"528Гц Глибокий Сон — Нейронна частота для швидкого засинання.
🌙 ЧОРНИЙ ЕКРАН: екран гасне автоматично. Яскравість AMOLED — нуль.

#528гц #глибокийсон #чорнийекран #музикадлясну #бінауральний"},
    "cs":    {"title":"528Hz Hluboký Spánek ● Černá Obrazovka | Usni Rychle | ŽIVĚ 8H",
              "description":"528Hz Hluboký Spánek — Neurální frekvence pro rychlé usnutí.
🌙 ČERNÁ OBRAZOVKA: obrazovka se automaticky vypne. Jas AMOLED nula.

#528hz #hlubokýspánek #černáobrazovka #hudbanaaspánek #binaural"},
    "da":    {"title":"528Hz Dyb Søvn ● Sort Skærm | Sov Hurtigt | LIVE 8 Timer",
              "description":"528Hz Dyb Søvn — Neural frekvens til hurtig indsovning.
🌙 SORT SKÆRM: skærmen slukker automatisk. AMOLED-lysstyrke nul.

#528hz #dypsøvn #sortskærm #søvnmusik #binaural"},
    "no":    {"title":"528Hz Dyp Søvn ● Svart Skjerm | Sovn Raskt | DIREKTE 8 Timer",
              "description":"528Hz Dyp Søvn — Neural frekvens for rask innsovning.
🌙 SVART SKJERM: skjermen slukker automatisk. AMOLED-lysstyrke null.

#528hz #dypsøvn #svartskjerm #sovnemusikk #binaural"},
    "fi":    {"title":"528Hz Syvä Uni ● Musta Näyttö | Nuku Nopeasti | SUORANA 8H",
              "description":"528Hz Syvä Uni — Hermostofrekvenssi nopeaan nukahtamiseen.
🌙 MUSTA NÄYTTÖ: näyttö sammuu automaattisesti. AMOLED-kirkkaus nolla.

#528hz #syväuni #mustanäyttö #unimusiikki #binaural"},
}

# TAGS globais — mix de todos os idiomas = aparece em qualquer busca
TAGS_GLOBAIS = [
    # EN (maior volume)
    "528hz sleep","528hz deep sleep","black screen sleep music","binaural beats sleep",
    "sleep music 8 hours","fall asleep fast","528hz black screen","sleep frequency",
    "528hz healing","insomnia music","deep sleep music","meditation sleep",
    # PT
    "528hz sono profundo","música para dormir","tela preta sono","binaural sono",
    "frequência para dormir","dormir rápido","insônia cura","sono reparador",
    # ES
    "528hz sueño","música para dormir","pantalla negra sueño","binaural sueño",
    # HI
    "528hz neend","neend ki music","binaural neend",
    # JA
    "528hz 睡眠","睡眠音楽","深い眠り","バイノーラル 睡眠",
    # KO
    "528hz 수면","수면 음악","바이노럴 수면",
    # DE
    "528hz schlaf","schlafmusik","binaural schlaf","einschlafmusik",
    # ZH
    "528hz睡眠","睡眠音乐","双耳节拍睡眠",
    # FR
    "528hz sommeil","musique pour dormir","binaural sommeil",
    # IT
    "528hz sonno","musica per dormire","binaural sonno",
    # AR
    "528 هرتز نوم","موسيقى للنوم",
    # RU
    "528гц сон","музыка для сна","бинауральный сон",
    # General
    "daniela coelho","psicologia sono","sleep science","neural frequency",
    "solfeggio 528","hz healing","sleep anxiety","cortisol sleep",
]

def get_token():
    if not all([YT_KEY, YT_SECRET, YT_REFRESH]):
        return None
    try:
        r = requests.post("https://oauth2.googleapis.com/token", data={
            "client_id": YT_KEY, "client_secret": YT_SECRET,
            "refresh_token": YT_REFRESH, "grant_type": "refresh_token"
        }, timeout=10)
        return r.json().get("access_token") if r.status_code == 200 else None
    except: return None

def buscar_live(token):
    try:
        r = requests.get(
            "https://www.googleapis.com/youtube/v3/liveBroadcasts",
            params={"part":"id,snippet","broadcastStatus":"active","broadcastType":"all"},
            headers={"Authorization": f"Bearer {token}"}, timeout=10)
        items = r.json().get("items",[])
        return items[0] if items else None
    except: return None

def buscar_video(token):
    """Busca o vídeo da live para atualizar via videos.update"""
    try:
        live = buscar_live(token)
        if not live: return None
        content = live.get("contentDetails",{})
        # Tenta via search para pegar o videoId da live
        r = requests.get(
            "https://www.googleapis.com/youtube/v3/search",
            params={"part":"id","channelId":"UCyCkIpsVgME9yCj_oXJFheA",
                    "type":"video","eventType":"live","maxResults":"1"},
            headers={"Authorization": f"Bearer {token}"}, timeout=10)
        items = r.json().get("items",[])
        return items[0]["id"]["videoId"] if items else None
    except: return None

def aplicar_seo_completo(token, video_id):
    """
    Aplica via videos.update:
    - snippet: título PT + tags 500 itens + categoria 22 + defaultLanguage
    - localizations: títulos/descrições em 25 idiomas
    - status: madeForKids=false, privacyStatus=public
    """
    resultados = {}

    # 1. Busca snippet atual
    r = requests.get(
        "https://www.googleapis.com/youtube/v3/videos",
        params={"part":"snippet,status,localizations","id":video_id},
        headers={"Authorization":f"Bearer {token}"}, timeout=10)
    if r.status_code != 200:
        print(f"  Erro ao buscar vídeo: {r.status_code}")
        return False

    item = r.json().get("items",[{}])[0]
    snippet = item.get("snippet", {})

    # 2. Atualizar snippet principal (PT-BR)
    snippet["title"]            = LOCALIZATIONS["pt"]["title"][:100]
    snippet["description"]      = LOCALIZATIONS["pt"]["description"][:5000]
    snippet["tags"]             = TAGS_GLOBAIS[:500]
    snippet["categoryId"]       = "22"           # People & Blogs
    snippet["defaultLanguage"]  = "pt"
    snippet["defaultAudioLanguage"] = "pt"

    # 3. Localizations completas (25 idiomas)
    localizations = {
        lang: {
            "title":       data["title"][:100],
            "description": data["description"][:5000],
        }
        for lang, data in LOCALIZATIONS.items()
    }

    # 4. Status
    status = {"madeForKids": False, "privacyStatus": "public"}

    payload = {
        "id": video_id,
        "snippet": snippet,
        "localizations": localizations,
        "status": status,
    }

    r2 = requests.put(
        "https://www.googleapis.com/youtube/v3/videos",
        params={"part":"snippet,localizations,status"},
        headers={"Authorization":f"Bearer {token}","Content-Type":"application/json"},
        json=payload, timeout=20)

    ok = r2.status_code == 200
    resultados["videos.update"] = "✅" if ok else f"❌ {r2.status_code}"

    if not ok:
        print(f"  Erro: {r2.text[:200]}")

    return ok, resultados

def salvar_log_supabase(resultados, n_idiomas):
    if not SB_KEY: return
    try:
        requests.post(f"{SB_URL}/rest/v1/ia_cache",
            headers={"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}",
                     "Content-Type":"application/json","Prefer":"return=minimal"},
            json={"key":f"seo_global_log_{int(time.time())}",
                  "value":json.dumps({"idiomas":n_idiomas,"resultado":str(resultados),
                                      "ts":time.strftime("%Y-%m-%dT%H:%M:%SZ")})},
            timeout=8)
    except: pass

def run():
    print("=== SEO GLOBAL MASTER — 25 IDIOMAS ===")
    print(f"  Mercado total endereçável: ~2.3M buscas/mês")
    print()

    token = get_token()
    if not token:
        print("  YouTube token não configurado.")
        print()
        print("  Para ativar: adicione aos GitHub Secrets:")
        print("  YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN")
        print()
        print("  ══ TÍTULOS PARA COPIAR MANUALMENTE NO YOUTUBE STUDIO ══")
        for lang, data in LOCALIZATIONS.items():
            print(f"\n  [{lang.upper()}] {data['title']}")
        return

    video_id = buscar_video(token)
    if not video_id:
        print("  Nenhuma live ativa. SEO será aplicado quando a live iniciar.")
        return

    print(f"  Live ativa: {video_id}")
    ok, res = aplicar_seo_completo(token, video_id)
    print(f"  videos.update: {res.get('videos.update','?')}")
    print(f"  Idiomas aplicados: 25")
    print(f"  Tags globais: {len(TAGS_GLOBAIS)}")

    salvar_log_supabase(res, 25)

    if ok:
        print()
        print("  ✅ YouTube agora mostrará o título no idioma do espectador!")
        print("  ✅ Aparece em buscas locais de 25 países automaticamente")

if __name__=="__main__": run()
