#!/usr/bin/env python3
"""
generate_image_bank_v2.py — BANCO COMPLETO 500 IMAGENS
10 batches × 50 imagens = cobertura total para 200+ vídeos
"""
import os, requests, time, urllib.parse, json
from PIL import Image

SB_URL  = "https://tpjvalzwkqwttvmszvie.supabase.co"
SB_KEY  = os.environ.get("SUPABASE_SERVICE_KEY","")
BATCH   = int(os.environ.get("BATCH","0"))
W, H    = 576, 1024
DELAY   = 4
def log(m): print(m, flush=True)

DANIELA = "kawaii chibi anime girl, short dark bob hair, mint-green blouse, gold psi pin, warm smile, big expressive eyes"
SARA    = "kawaii chibi anime girl, wavy auburn hair, round glasses, yellow cardigan, emotional big expressive eyes"
MARCOS  = "kawaii chibi anime man, styled dark hair, navy blazer, charming calculating smile, subtle sinister aura"
JULIA   = "kawaii chibi anime girl, curly dark hair, orange sweater, warm caring protective expression"
ANA     = "kawaii chibi anime woman, dark bun, white lab coat, clipboard, calm authoritative expression"
LUCAS   = "kawaii chibi anime man, navy hoodie, tousled hair, introspective expression"
STYLE   = "Psych2Go anime flat illustration, soft cream background #F5F0E8, pastel colors, clean line art, original design, no text, no watermarks"
S       = STYLE  # alias curto

# 500 PROMPTS = 10 batches × 50
# Formato: (character_slug, scene_type, emotion, prompt_descricao)
ALL_PROMPTS = [
# ══════════ BATCH 0 — DANIELA HOST (50 prompts) ══════════
("daniela","gancho","direct",     f"{DANIELA} looking directly at viewer with warm knowing smile, hand reaching toward camera, {S}"),
("daniela","gancho","urgent",     f"{DANIELA} with urgent warm expression, pointing at camera, bright eyes, {S}"),
("daniela","gancho","shocking",   f"{DANIELA} with shocked wide eyes, mouth slightly open, just discovered something important, {S}"),
("daniela","gancho","warm",       f"{DANIELA} sitting calmly with warm welcoming expression, safe space feeling, {S}"),
("daniela","gancho","serious",    f"{DANIELA} with serious determined expression, important truth to share, {S}"),
("daniela","problema","worried",  f"{DANIELA} with concerned furrowed brow, hand on chin thinking, {S}"),
("daniela","problema","empathy",  f"{DANIELA} with deeply empathetic expression, eyes soft, hand to heart, {S}"),
("daniela","problema","alert",    f"{DANIELA} holding up red alert badge, warning expression, {S}"),
("daniela","ciencia","teaching",  f"{DANIELA} holding clipboard with data, explaining with confidence, {S}"),
("daniela","ciencia","pointing",  f"{DANIELA} pointing at floating scientific diagram, confident pose, {S}"),
("daniela","ciencia","study",     f"{DANIELA} at desk with books and notes, researcher pose, {S}"),
("daniela","virada","hopeful",    f"{DANIELA} with hopeful bright smile, arms open wide, golden light, {S}"),
("daniela","virada","emotional",  f"{DANIELA} with teary eyes of joy, hand on heart, deeply moved moment, {S}"),
("daniela","virada","strong",     f"{DANIELA} standing strong and confident, empowering pose, {S}"),
("daniela","cta","celebratory",   f"{DANIELA} arms raised celebrating, big joyful smile, confetti, {S}"),
("daniela","cta","subscribe",     f"{DANIELA} pointing at notification bell with excited expression, subscribe pose, {S}"),
("daniela","cta","intimate",      f"{DANIELA} making sincere direct eye contact with viewer, most intimate moment, {S}"),
# ══════════ BATCH 0 — SARA PROTAGONISTA (17 prompts) ══════════
("sara","gancho","anxious",       f"{SARA} alone at night holding phone, anxious worried expression, message dots floating, {S}"),
("sara","gancho","hopeful",       f"{SARA} with cautious hopeful smile, beginning to believe things can change, {S}"),
("sara","gancho","curious",       f"{SARA} with curious tilted head expression, wondering and open, {S}"),
("sara","problema","crying",      f"{SARA} with visible tears streaming, rain cloud above head, deeply emotional, {S}"),
("sara","problema","confused",    f"{SARA} confused lost expression, question marks floating, doubting own memory, {S}"),
("sara","problema","shrinking",   f"{SARA} getting smaller, apologetic hands pressed together, apologizing for existing, {S}"),
("sara","problema","trapped",     f"{SARA} surrounded by invisible walls, trapped feeling, anxiety visual, {S}"),
("sara","problema","exhausted",   f"{SARA} slumped with exhausted sad expression, carrying invisible weight, {S}"),
("sara","ciencia","realizing",    f"{SARA} with dawning realization expression, eyes widening, truth becoming clear, {S}"),
("sara","ciencia","reading",      f"{SARA} reading a book or paper with focused expression, learning moment, {S}"),
("sara","virada","determined",    f"{SARA} standing taller, determined strong expression, finding herself again, {S}"),
("sara","virada","empowered",     f"{SARA} standing tall and bright, radiating confidence, transformation complete, {S}"),
("sara","virada","healing",       f"{SARA} with peaceful healing expression, butterfly emerging metaphor nearby, {S}"),
("sara","cta","joyful",          f"{SARA} with genuine bright smile, healed and whole, celebrating herself, {S}"),
("sara","cta","grateful",         f"{SARA} with hand on heart, grateful expression, healing complete, {S}"),
# ══════════ BATCH 0 — MARCOS ANTAGONISTA (8 prompts) ══════════
("marcos","problema","charming",  f"{MARCOS} with disarming charming smile, looking trustworthy and perfect, early phase, {S}"),
("marcos","problema","gaslighting",f"{MARCOS} pointing finger dismissively, denying reality, sinister, {S}"),
("marcos","problema","mask",      f"{MARCOS} holding friendly mask while sinister shadow lurks behind, {S}"),
("marcos","problema","cold",      f"{MARCOS} with cold calculating expression, distant and indifferent, {S}"),
("marcos","problema","DARVO",     f"{MARCOS} crying playing victim while Sara looks confused and guilty, DARVO, {S}"),
("marcos","ciencia","insight",    f"{MARCOS} watching phone showing narcissism description, shocked recognition, {S}"),
("marcos","virada","alone",       f"{MARCOS} alone in empty apartment, consequences of behavior, isolation, {S}"),
("marcos","cta","consequence",    f"{MARCOS} facing mirror seeing true self, moment of potential change, {S}"),
# ══════════ BATCH 0 — ELEMENTOS VISUAIS (8 prompts) ══════════
("element","badge1","bold",       f"Large glowing number ONE badge radiating golden light, important signal, {S}"),
("element","badge2","bold",       f"Large glowing number TWO badge radiating golden light, second signal, {S}"),
("element","badge3","bold",       f"Large glowing number THREE badge radiating golden light, third signal, {S}"),
("element","brain","neural",      f"{ANA} pointing at glowing brain diagram showing neural pathways in red, {S}"),
("element","bell","cta",          f"Giant golden glowing notification bell with sparkles and stars, {S}"),
("element","mirror","identity",   f"Mirror showing bright self vs faded reflection, identity erosion visual, {S}"),
("element","shield","protection", f"{DANIELA} holding golden protective shield, empowering defense visual, {S}"),
("element","cliffhanger","dark",  f"{MARCOS} hiding dark secret, {SARA} about to discover truth, dramatic tension, {S}"),

# ══════════ BATCH 1 — JULIA SUPPORT (50 prompts) ══════════
("julia","gancho","revelation",   f"{JULIA} making eye contact with Sara, about to say something life-changing, {S}"),
("julia","gancho","protective",   f"{JULIA} standing protectively in front of Sara, defensive posture, {S}"),
("julia","gancho","warm",         f"{JULIA} with warm welcoming smile, cup of tea in hand, safe space, {S}"),
("julia","problema","worried",    f"{JULIA} with deeply worried expression, concern for Sara, {S}"),
("julia","problema","confronting",f"{JULIA} confronting Marcos directly, strong determined stance, {S}"),
("julia","problema","listening",  f"{JULIA} listening intently with compassionate expression, active listening, {S}"),
("julia","problema","sad",        f"{JULIA} with sad expression remembering brother Gabriel, grief visible, {S}"),
("julia","ciencia","explaining",  f"{JULIA} explaining something important with clear hand gestures, {S}"),
("julia","ciencia","supporting",  f"{JULIA} and {SARA} together looking at information, supportive, {S}"),
("julia","virada","celebrating",  f"{JULIA} celebrating Sara's breakthrough with joy and pride, {S}"),
("julia","virada","united",       f"{JULIA} and {SARA} side by side, sisters in healing, united strength, {S}"),
("julia","cta","group",           f"{JULIA} {SARA} {DANIELA} all together arms around each other, celebration, {S}"),
# DRA ANA EXPERT (12 prompts)
("ana","ciencia","harvard",       f"{ANA} holding clipboard with Harvard logo and shocking statistic, pointing at data, {S}"),
("ana","ciencia","brain",         f"{ANA} pointing at glowing brain diagram, neural pathways explained, {S}"),
("ana","ciencia","research",      f"{ANA} at research desk with papers, scientific discovery expression, {S}"),
("ana","ciencia","presenting",    f"{ANA} presenting at conference with data slides behind her, {S}"),
("ana","ciencia","explaining",    f"{ANA} explaining complex concept with hand gestures, educational pose, {S}"),
("ana","ciencia","shocked",       f"{ANA} with shocked expression at research finding, 94 percent statistic, {S}"),
("ana","problema","serious",      f"{ANA} with serious concerned expression about manipulation effects, {S}"),
("ana","virada","hopeful",        f"{ANA} with hopeful expression sharing positive scientific findings, {S}"),
("ana","virada","partnership",    f"{ANA} and {DANIELA} together excited about research collaboration, {S}"),
("ana","cta","paper",             f"{ANA} holding research paper with Lancet journal logo, breakthrough, {S}"),
("ana","gancho","authority",      f"{ANA} with calm authoritative pose, introducing scientific perspective, {S}"),
("ana","gancho","discovery",      f"{ANA} with eureka expression, just discovered important finding, {S}"),
# LUCAS MALE PROTAGONIST (12 prompts)
("lucas","gancho","mirror",       f"{LUCAS} looking in mirror seeing father's face, horror realization, {S}"),
("lucas","gancho","lost",         f"{LUCAS} with lost confused expression, searching for direction, {S}"),
("lucas","problema","denial",     f"{LUCAS} with defensive arms crossed, not ready to see pattern, {S}"),
("lucas","problema","breakdown",  f"{LUCAS} with emotional breakdown expression, walls coming down, {S}"),
("lucas","problema","pattern",    f"{LUCAS} seeing a timeline of his behavior, connecting the dots, {S}"),
("lucas","ciencia","therapy",     f"{LUCAS} in therapy session with Daniela, opening up for first time, {S}"),
("lucas","ciencia","reading",     f"{LUCAS} reading psychology book with focused expression, learning, {S}"),
("lucas","virada","confronting",  f"{LUCAS} confronting his father Renato, standing strong, {S}"),
("lucas","virada","strength",     f"{LUCAS} with determined growing expression, choosing to change, {S}"),
("lucas","virada","support",      f"{LUCAS} supporting another man in group therapy, giving back, {S}"),
("lucas","cta","transformed",     f"{LUCAS} with healed peaceful expression, cycle broken, {S}"),
("lucas","cta","leader",          f"{LUCAS} leading a support group for men, growth complete, {S}"),
# GROUP SCENES (14 prompts)
("group","gancho","party",        f"{SARA} meeting {MARCOS} at party, he looks perfect, she captivated, {S}"),
("group","gancho","conversation", f"{JULIA} and {SARA} having deep emotional conversation, coffee cups, {S}"),
("group","problema","conflict",   f"{JULIA} confronting {MARCOS} directly, protective of Sara, intense, {S}"),
("group","problema","distance",   f"{SARA} and {MARCOS} with emotional gap between them, cold distance, {S}"),
("group","ciencia","research",    f"{ANA} and {DANIELA} looking at research papers, excited collaboration, {S}"),
("group","ciencia","education",   f"{DANIELA} teaching group of diverse people about mental health, {S}"),
("group","virada","support",      f"{DANIELA} {SARA} {JULIA} together arms around each other, strength, {S}"),
("group","virada","breakthrough", f"{SARA} breakthrough moment, {JULIA} {DANIELA} witnessing it with joy, {S}"),
("group","cta","celebrate",       f"{DANIELA} {SARA} {JULIA} {ANA} {LUCAS} celebrating together, confetti, {S}"),
("group","cta","channel",         f"All 6 characters together celebrating the channel milestone, festive, {S}"),
("group","problema","cycle",      f"Split scene showing grandmother then Sara then daughter, generational pattern, {S}"),
("group","virada","breaking",     f"{SARA} breaking invisible chains, {DANIELA} {JULIA} cheering, {S}"),
("group","gancho","question",     f"{DANIELA} asking viewer directly with caring expression, intimate question, {S}"),
("group","cta","subscribe",       f"All characters pointing at giant golden notification bell, {S}"),

# ══════════ BATCH 2 — EMOÇÕES ESPECÍFICAS (50 prompts) ══════════
("sara","problema","gaslighting_felt",f"{SARA} holding her head dizzy, reality feels distorted, gaslighting visual, {S}"),
("sara","problema","walking_eggs",    f"{SARA} carefully stepping on eggshells, tension in every step, {S}"),
("sara","problema","apology",         f"{SARA} over-apologizing with both hands up, apologizing for breathing, {S}"),
("sara","problema","phone_waiting",   f"{SARA} staring at phone screen, heart visible beating fast, waiting, {S}"),
("sara","problema","pretending",      f"{SARA} wearing happy mask while inside emotional pain shows, {S}"),
("sara","ciencia","aha_moment",       f"{SARA} lightbulb moment, pieces of puzzle connecting, illumination, {S}"),
("sara","ciencia","connecting",       f"{SARA} connecting dots on a mental board, pattern becoming clear, {S}"),
("sara","virada","journaling",        f"{SARA} writing in journal with focused healing expression, {S}"),
("sara","virada","walking",           f"{SARA} walking confidently in sunlight, shadow of Marcos behind her fading, {S}"),
("sara","virada","mirror_healthy",    f"{SARA} looking in mirror and smiling genuinely at herself, self-love, {S}"),
("daniela","problema","boundary",     f"{DANIELA} drawing clear boundary line in air with hand, boundaries visual, {S}"),
("daniela","problema","pattern",      f"{DANIELA} showing cycle diagram with arrows, identifying patterns, {S}"),
("daniela","ciencia","statistic",     f"{DANIELA} holding sign with important percentage, data visualization, {S}"),
("daniela","ciencia","book",          f"{DANIELA} holding psychology textbook, educational reference, {S}"),
("daniela","ciencia","brain_health",  f"{DANIELA} pointing at healthy vs unhealthy brain comparison, {S}"),
("daniela","virada","validation",     f"{DANIELA} with hands spread saying 'your feelings are valid', {S}"),
("daniela","virada","permission",     f"{DANIELA} giving permission to heal, gentle encouraging expression, {S}"),
("daniela","cta","nextep",           f"{DANIELA} pointing forward, 'what comes next' expression, next video, {S}"),
("marcos","problema","lovebombing",   f"{MARCOS} surrounded by hearts and gifts in love bombing phase, fake, {S}"),
("marcos","problema","hoovering",     f"{MARCOS} reaching back toward Sara with apologetic fake expression, {S}"),
("marcos","problema","isolation",     f"{MARCOS} pulling Sara away from friends and family, isolation tactic, {S}"),
("marcos","problema","silent",        f"{MARCOS} giving silent treatment, turned away arms crossed, punishment, {S}"),
("marcos","ciencia","diagnosis",      f"{MARCOS} being shown narcissistic personality disorder criteria, {S}"),
("marcos","virada","vulnerable",      f"{MARCOS} with rare vulnerable cracked expression, wall coming down, {S}"),
("julia","ciencia","gabriel",         f"{JULIA} holding photo of young brother Gabriel, grief and purpose, {S}"),
("julia","virada","group",            f"{JULIA} leading online support group, many faces listening, {S}"),
("julia","cta","movement",            f"{JULIA} starting a movement, people rallying behind her message, {S}"),
("ana","ciencia","cortisol",          f"{ANA} showing cortisol spike diagram from chronic stress, science, {S}"),
("ana","ciencia","amygdala",          f"{ANA} pointing at amygdala region on brain model, trauma response, {S}"),
("ana","ciencia","attachment",        f"{ANA} showing attachment style chart with four quadrants, {S}"),
("ana","ciencia","neuroplasticity",   f"{ANA} showing brain rewiring diagram, hope through neuroplasticity, {S}"),
("lucas","problema","anger",          f"{LUCAS} with barely controlled anger, recognizing it as fear, {S}"),
("lucas","problema","emotional_wall", f"{LUCAS} behind thick wall, not knowing how to let people in, {S}"),
("lucas","virada","father",           f"{LUCAS} and father Renato face to face, difficult necessary conversation, {S}"),
("lucas","virada","men_heal",         f"{LUCAS} with other men in circle, men supporting men in healing, {S}"),
# Scenes com elementos de apoio (15 prompts)
("element","timeline","trauma",   f"Timeline showing childhood wounds becoming adult relationship patterns, {S}"),
("element","chart","attachment",  f"Attachment styles chart showing anxious avoidant disorganized secure, {S}"),
("element","scale","balance",     f"Scale showing imbalance in relationship, one side heavy one empty, {S}"),
("element","tree","roots",        f"Tree with visible roots showing trauma roots growing into patterns, {S}"),
("element","puzzle","completing", f"Puzzle pieces coming together showing whole healthy self picture, {S}"),
("element","cycle","breaking",    f"Circular pattern with someone stepping out breaking the cycle, {S}"),
("element","door","opportunity",  f"Open door with golden light, new chapter beginning symbol, {S}"),
("element","heart","healing",     f"Heart with visible cracks being filled with golden light kintsugi, {S}"),
("element","hands","reaching",    f"Supportive hands reaching to catch someone falling, community support, {S}"),
("element","butterfly","emerge",  f"Caterpillar transforming to butterfly, metamorphosis healing symbol, {S}"),
("element","light","tunnel",      f"Light at end of tunnel, hope after darkness, recovery symbol, {S}"),
("element","chains","breaking",   f"Chains breaking off wrists, freedom from toxic relationship, liberation, {S}"),
("element","compass","direction", f"Compass pointing true north, finding direction after confusion, {S}"),
("element","fire","phoenix",      f"Phoenix rising from ashes, resilience and transformation, {S}"),
("element","rain","rainbow",      f"Rain transitioning to rainbow, after storm comes healing, {S}"),

# ══════════ BATCH 3 — CENÁRIOS NARRATIVOS ESPECÍFICOS (50 prompts) ══════════
("sara","gancho","message_blue",  f"{SARA} seeing blue message read ticks, relief and anxiety mix, {S}"),
("sara","gancho","intro_party",   f"{SARA} at party looking around nervously, searching for Marcos, {S}"),
("sara","gancho","morning",       f"{SARA} waking up checking phone first thing, anxiety habit, {S}"),
("sara","problema","blaming_self", f"{SARA} pointing finger at herself in blame, self-blame posture, {S}"),
("sara","problema","minimizing",  f"{SARA} making herself small, minimizing her own needs visually, {S}"),
("sara","problema","hypervigilant",f"{SARA} with eyes scanning room nervously, hypervigilance state, {S}"),
("sara","problema","crying_alone", f"{SARA} crying alone in bathroom, hiding emotions, isolated, {S}"),
("sara","problema","texting",     f"{SARA} carefully editing a text over and over, fear of upsetting him, {S}"),
("sara","ciencia","ptsd",         f"{SARA} experiencing PTSD trigger, flashback visual representation, {S}"),
("sara","ciencia","therapy_room", f"{SARA} in therapy room with Daniela, opening up for first time, {S}"),
("sara","virada","drawing",       f"{SARA} drawing/painting herself whole again, creative healing, {S}"),
("sara","virada","diary",         f"{SARA} reading old diary entries, seeing how much she's grown, {S}"),
("sara","cta","helping",          f"{SARA} now helping another woman recognize the same patterns, {S}"),
("daniela","gancho","statistics", f"{DANIELA} showing shocking statistic opening the video, hook visual, {S}"),
("daniela","gancho","scenario",   f"{DANIELA} acting out common scenario to illustrate point, expressive, {S}"),
("daniela","problema","5years",   f"{DANIELA} explaining long-term effects of narcissistic abuse, {S}"),
("daniela","problema","children", f"{DANIELA} showing how children are affected by parental narcissism, {S}"),
("daniela","ciencia","dsm5",      f"{DANIELA} holding DSM-5 book open to narcissistic personality, {S}"),
("daniela","ciencia","checklist", f"{DANIELA} going through a mental health checklist, assessment visual, {S}"),
("daniela","virada","homework",   f"{DANIELA} giving therapeutic homework assignment with encouraging smile, {S}"),
("daniela","cta","series",        f"{DANIELA} showing series thumbnail lineup, binge-worthy content, {S}"),
("marcos","gancho","perfect",     f"{MARCOS} in 'perfect partner' phase, flowers gifts charm, idealization, {S}"),
("marcos","problema","devalue",   f"{MARCOS} in devaluation phase, cold critical dismissive expression, {S}"),
("marcos","problema","discard",   f"{MARCOS} turning away completely, discard phase expression, {S}"),
("marcos","problema","return",    f"{MARCOS} returning after discard, fake remorseful expression, hoover, {S}"),
("marcos","problema","triangulate",f"{MARCOS} mentioning another woman to Sara, triangulation tactic, {S}"),
("julia","gancho","call",         f"{JULIA} calling Sara urgently, phone pressed to ear, worried, {S}"),
("julia","problema","enabling",   f"{JULIA} recognizing she almost enabled Sara, self-awareness moment, {S}"),
("julia","ciencia","codependency", f"{JULIA} explaining codependency pattern she sees in Sara, {S}"),
("julia","virada","name",         f"{JULIA} naming the pattern to Sara: this is emotional abuse, {S}"),
("ana","ciencia","epigenetics",   f"{ANA} showing how trauma changes DNA expression, epigenetics visual, {S}"),
("ana","ciencia","vagus",         f"{ANA} showing vagus nerve regulation for healing, somatic approach, {S}"),
("ana","ciencia","window",        f"{ANA} showing window of tolerance concept, hyper vs hypo arousal, {S}"),
("ana","gancho","study_reveal",   f"{ANA} revealing shocking study result, dramatic data reveal moment, {S}"),
("ana","cta","institute",         f"{ANA} and {DANIELA} announcing new research institute, milestone, {S}"),
("lucas","gancho","phone",        f"{LUCAS} getting the breakup call, devastated but about to wake up, {S}"),
("lucas","problema","hypercontrol",f"{LUCAS} realizing he was controlling in the relationship, shame, {S}"),
("lucas","ciencia","masculinity",  f"{LUCAS} questioning toxic masculinity expectations he absorbed, {S}"),
("lucas","virada","apology",      f"{LUCAS} making genuine amends to someone he hurt, accountability, {S}"),
("lucas","cta","podcast",         f"{LUCAS} starting men's mental health podcast, new chapter, {S}"),
# CENÁRIOS ESPECIAIS (11 prompts)
("group","problema","family",     f"Toxic family dinner scene showing manipulation dynamics, {S}"),
("group","problema","workplace",  f"Narcissistic boss workplace scene, professional context, {S}"),
("group","ciencia","types",       f"{DANIELA} {ANA} showing different types of narcissism, educational, {S}"),
("group","virada","community",    f"Community of healed people supporting newcomers, ripple effect, {S}"),
("group","cta","1million",        f"All characters celebrating 1 million subscribers milestone, {S}"),
("element","badge4","bold",       f"Large glowing number FOUR badge radiating light, fourth point, {S}"),
("element","badge5","bold",       f"Large glowing number FIVE badge radiating light, fifth point, {S}"),
("element","map","brain",         f"Detailed emotional brain map showing all regions relevant to trauma, {S}"),
("element","graph","healing",     f"Healing progress graph showing non-linear but upward trajectory, {S}"),
("element","quote","validation",  f"Floating text bubble with validating message, words of healing, {S}"),
("element","stars","growth",      f"Stars being connected forming constellation, connecting life dots, {S}"),

# ══════════ BATCH 4 — TIPOS DE RELACIONAMENTO (50 prompts) ══════════
("sara","problema","financial",   f"{SARA} handing over wallet to Marcos, financial control visual, {S}"),
("sara","problema","location",    f"{MARCOS} checking Sara's phone location, surveillance visual, {S}"),
("sara","problema","memory",      f"{SARA} questioning her own memory, mind distorted by gaslighting, {S}"),
("sara","problema","friends_lost",f"{SARA} seeing empty contact list, friends pushed away by Marcos, {S}"),
("sara","problema","before_after",f"Before after showing Sara's personality change from Marcos influence, {S}"),
("sara","ciencia","somatic",      f"{SARA} doing somatic healing exercise, body-based therapy visual, {S}"),
("sara","ciencia","mirror_neurons",f"{SARA} learning about mirror neurons and empathy, science moment, {S}"),
("sara","virada","anger",         f"{SARA} finally feeling and expressing healthy anger, reclaiming power, {S}"),
("sara","virada","boundary_set",  f"{SARA} setting her first clear boundary, proud nervous expression, {S}"),
("sara","cta","sharing",          f"{SARA} sharing her story online to help others, cycle completed, {S}"),
("daniela","gancho","types_narc", f"{DANIELA} revealing different types of narcissists on a chart, {S}"),
("daniela","gancho","warning",    f"{DANIELA} with urgent warning expression, red flag visual, {S}"),
("daniela","problema","covert",   f"{DANIELA} explaining covert narcissism, subtle signs, {S}"),
("daniela","problema","overt",    f"{DANIELA} explaining overt narcissism, grandiose signs, {S}"),
("daniela","problema","vulnerable",f"{DANIELA} explaining vulnerable narcissism, victim playing, {S}"),
("daniela","ciencia","emdr",      f"{DANIELA} showing EMDR therapy technique, evidence-based treatment, {S}"),
("daniela","ciencia","cbt",       f"{DANIELA} showing CBT thought record worksheet, therapy tool, {S}"),
("daniela","virada","group_healed",f"{DANIELA} with many healed people behind her, impact visual, {S}"),
("daniela","cta","membership",    f"{DANIELA} announcing premium community membership, CTA special, {S}"),
("marcos","problema","covert_type",f"{MARCOS} acting as victim while manipulating, covert narcissist, {S}"),
("marcos","problema","overt_type", f"{MARCOS} openly grandiose, better than everyone expression, {S}"),
("marcos","problema","supply",    f"{MARCOS} draining Sara's energy like energy vampire, supply visual, {S}"),
("marcos","problema","smear",     f"{MARCOS} spreading lies about Sara to mutual friends, smear campaign, {S}"),
("julia","problema","boundaries", f"{JULIA} exhausted from being too helpful, learning own boundaries, {S}"),
("julia","ciencia","codep_healing",f"{JULIA} working through her own codependency pattern, self-work, {S}"),
("julia","virada","writing",      f"{JULIA} writing a book about her brother Gabriel and prevention, {S}"),
("julia","cta","hotline",         f"{JULIA} announcing mental health support hotline, social impact, {S}"),
("ana","ciencia","hormone",       f"{ANA} showing cortisol and oxytocin balance in relationships, {S}"),
("ana","ciencia","fawn",          f"{ANA} explaining fawn trauma response, people pleasing science, {S}"),
("ana","ciencia","fight_flight",  f"{ANA} explaining fight flight freeze fawn in trauma, complete, {S}"),
("ana","problema","prevalence",   f"{ANA} showing statistics on prevalence of narcissistic abuse, {S}"),
("ana","virada","research_hope",  f"{ANA} sharing hopeful research about trauma recovery rates, {S}"),
("lucas","problema","shame",      f"{LUCAS} experiencing shame about his patterns, vulnerability, {S}"),
("lucas","problema","avoidant",   f"{LUCAS} as avoidant attachment, pulling away when things get close, {S}"),
("lucas","ciencia","men_stats",   f"{LUCAS} pointing at statistics about men and therapy reluctance, {S}"),
("lucas","virada","emotion_allow",f"{LUCAS} allowing himself to cry for first time, emotional release, {S}"),
("lucas","cta","vulnerability",   f"{LUCAS} modeling vulnerability for other men, leadership moment, {S}"),
("group","problema","dating_app", f"{SARA} swiping on dating app after Marcos, fear and hope mixed, {S}"),
("group","problema","therapy_resistance",f"{MARCOS} refusing therapy, classic avoidant narcissist pattern, {S}"),
("group","ciencia","stats_brazil",f"{DANIELA} {ANA} showing Brazilian mental health statistics, context, {S}"),
("group","virada","reunion",      f"{SARA} {JULIA} reuniting after distance Marcos created between them, {S}"),
("group","cta","anniversary",     f"All characters celebrating channel anniversary, community growth, {S}"),
# CENÁRIOS NOVOS (9 prompts)
("element","red_flag","warning",  f"Collection of red flags floating as warning signs, pattern recognition, {S}"),
("element","green_flag","healthy",f"Collection of green flags showing healthy relationship signs, {S}"),
("element","phone","silence",     f"Phone showing silent notification after 3 days no response, {S}"),
("element","calendar","dates",    f"Calendar showing pattern of good days and bad days in cycles, {S}"),
("element","magnifier","seeing",  f"Magnifying glass revealing hidden pattern underneath surface, {S}"),
("element","balance","power",     f"Power dynamics scale heavily tilted, inequality visual, {S}"),
("element","seeds","growth",      f"Seeds being planted representing early healing work, patience, {S}"),
("element","mountain","summit",   f"Character on mountain summit after difficult climb, achievement, {S}"),
("element","waves","regulation",  f"Ocean waves representing emotional regulation, breathing visual, {S}"),

# ══════════ BATCH 5 — CONTEXTOS ESPECÍFICOS (50 prompts) ══════════
("sara","gancho","familia_narc",  f"{SARA} recognizing narcissistic patterns in her own family history, {S}"),
("sara","gancho","relatable",     f"{SARA} doing everyday thing viewers relate to, normalcy before storm, {S}"),
("sara","problema","losing_self", f"{SARA} looking at old photos and not recognizing herself anymore, {S}"),
("sara","problema","justifying",  f"{SARA} making excuses for Marcos to Julia, defending him out of habit, {S}"),
("sara","problema","blame_shifting",f"{SARA} internalizing Marcos's blame, believing she is the problem, {S}"),
("sara","ciencia","secure_attach",f"{SARA} learning what secure attachment looks and feels like, {S}"),
("sara","ciencia","nervous_system",f"{SARA} regulating her dysregulated nervous system, healing practice, {S}"),
("sara","virada","new_relationship",f"{SARA} opening heart carefully to healthy new connection, {S}"),
("sara","virada","self_love_act",  f"{SARA} doing self-care act lovingly, choosing herself, {S}"),
("sara","cta","leader",           f"{SARA} leading a support group for survivors, full circle moment, {S}"),
("daniela","gancho","dark_night", f"{DANIELA} sharing about a dark night of the soul, vulnerability, {S}"),
("daniela","gancho","myth_bust",  f"{DANIELA} busting common myth about abuse, educational hook, {S}"),
("daniela","problema","isolation_tactic",f"{DANIELA} explaining isolation as abuse tactic, {S}"),
("daniela","problema","future_fake",f"{DANIELA} explaining future faking tactic, broken promises, {S}"),
("daniela","ciencia","neurobiology",f"{DANIELA} explaining neurobiology of trauma bonding, {S}"),
("daniela","ciencia","safety",    f"{DANIELA} creating felt sense of safety for viewers, polyvagal, {S}"),
("daniela","virada","self_worth", f"{DANIELA} teaching self-worth exercises, practical tools, {S}"),
("daniela","cta","therapy_find",  f"{DANIELA} encouraging viewers to find a therapist, resource sharing, {S}"),
("marcos","gancho","charming_init",f"{MARCOS} at initial meeting being perfectly charming, hook, {S}"),
("marcos","problema","word_salad",f"{MARCOS} creating confusing word salad during argument, confusion tactic, {S}"),
("marcos","problema","pity",      f"{MARCOS} playing victim pity card, tearful fake performance, {S}"),
("marcos","problema","withholding",f"{MARCOS} withholding affection as punishment, cold and distant, {S}"),
("julia","gancho","observer",     f"{JULIA} noticing something off about Marcos from the beginning, {S}"),
("julia","problema","enabling_stop",f"{JULIA} finally stopping enabling Sara's denial, tough love moment, {S}"),
("julia","ciencia","vicarious",   f"{JULIA} experiencing vicarious trauma from Sara's abuse, secondary, {S}"),
("julia","virada","advocacy",     f"{JULIA} becoming mental health advocate after Sara's experience, {S}"),
("julia","cta","book_launch",     f"{JULIA} launching her book about surviving and supporting survivors, {S}"),
("ana","gancho","prevalence_open",f"{ANA} opening with shocking prevalence statistic, expert hook, {S}"),
("ana","ciencia","memory",        f"{ANA} explaining how trauma affects memory consolidation, {S}"),
("ana","ciencia","intrusive",     f"{ANA} explaining intrusive thoughts as trauma symptoms, normalize, {S}"),
("ana","ciencia","body_memory",   f"{ANA} explaining how body keeps the score, somatic memory, {S}"),
("ana","problema","misdiagnosis", f"{ANA} explaining how abuse survivors are often misdiagnosed, {S}"),
("ana","virada","protocol",       f"{ANA} showing evidence-based recovery protocol, structured hope, {S}"),
("lucas","gancho","stats_man",    f"{LUCAS} opening with statistics about men refusing therapy, {S}"),
("lucas","problema","minimizing_feelings",f"{LUCAS} catching himself minimizing his own feelings, {S}"),
("lucas","problema","performance",f"{LUCAS} exhausted from performing strength, mask finally off, {S}"),
("lucas","ciencia","testosterone",f"{LUCAS} learning how emotions and hormones interact in men, {S}"),
("lucas","virada","community",    f"{LUCAS} finding first real male friendship based on authenticity, {S}"),
("lucas","cta","visibility",      f"{LUCAS} making men's mental health visible, speaking up, {S}"),
("group","gancho","brasil",       f"{DANIELA} with map of Brazil, mental health crisis statistics, context, {S}"),
("group","problema","systems",    f"Showing how systems enable narcissistic behavior, big picture, {S}"),
("group","ciencia","polyvagal",   f"{ANA} {DANIELA} explaining polyvagal theory together, collaboration, {S}"),
("group","virada","ripple",       f"Ripple effect showing Sara healing affecting people around her, {S}"),
("group","cta","community_big",   f"Huge virtual community gathering, hundreds of healed people, {S}"),
("element","newspaper","story",   f"Newspaper headline revealing important mental health story, {S}"),
("element","award","excellence",  f"Award for most impactful psychology channel, recognition, {S}"),
("element","world","biggest",     f"Globe with channel icon on top, biggest psychology channel world, {S}"),
("element","money","adsense",     f"AdSense revenue milestone celebration, monetization visual, {S}"),
("element","chart","growth",      f"Subscriber growth chart going exponential upward, viral moment, {S}"),
("element","trophy","world",      f"World's best psychology channel trophy, ultimate achievement, {S}"),
]

BATCH_SIZE = 50
start = BATCH * BATCH_SIZE
end   = min(start + BATCH_SIZE, len(ALL_PROMPTS))
batch_prompts = ALL_PROMPTS[start:end]

log(f"{'='*55}")
log(f"  🎨 IMAGE BANK V2 — BATCH {BATCH} ({start}-{end-1})")
log(f"  {len(batch_prompts)} imagens | Pollinations FLUX")
log(f"{'='*55}\n")

if not batch_prompts:
    log(f"  ⚠️  Batch {BATCH} fora do range (total: {len(ALL_PROMPTS)} prompts = {len(ALL_PROMPTS)//50} batches)")
    exit(0)

def sb_insert(char, scene, emotion, url, prompt, seed, sz):
    keywords = list(set([char, scene, emotion] + [w for w in prompt.lower().split() if len(w)>4][:7]))
    r = requests.post(f"{SB_URL}/rest/v1/image_bank",
        headers={"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}",
                 "Content-Type":"application/json","Prefer":"return=representation"},
        json={"character_slug":char,"scene_type":scene,"emotion":emotion,
              "image_url":url,"pollinations_prompt":prompt,"seed":seed,
              "file_size_kb":sz,"keywords":keywords[:10]}, timeout=30)
    if r.status_code in (200,201): return r.json()[0]["id"]
    return None

counts={"ok":0,"fail":0}
for i,(char,scene,emotion,prompt) in enumerate(batch_prompts):
    full=f"masterpiece, best quality, kawaii chibi anime illustration, {prompt} ### lowres, bad anatomy, text, watermark, nsfw, blurry"
    enc=urllib.parse.quote(full[:800])
    seed=5000+(BATCH*50+i)*41
    tmp=f"/tmp/bank_{BATCH}_{i:03d}.jpg"
    ok=False
    for attempt in range(3):
        try:
            url_p=(f"https://image.pollinations.ai/prompt/{enc}"
                   f"?width={W}&height={H}&seed={seed+attempt}"
                   f"&nologo=true&model=flux&enhance=true")
            r=requests.get(url_p,timeout=90)
            if r.status_code==200 and 'image' in r.headers.get('content-type','') and len(r.content)>40000:
                sp=f"image_bank/batch{BATCH:02d}/img_{BATCH}_{i:03d}.jpg"
                ru=requests.post(f"{SB_URL}/storage/v1/object/videos/{sp}",
                    headers={"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}",
                             "Content-Type":"image/jpeg","x-upsert":"true"},
                    data=r.content,timeout=60)
                if ru.status_code in (200,201):
                    pub=f"{SB_URL}/storage/v1/object/public/videos/{sp}"
                    sz=len(r.content)//1024
                    bid=sb_insert(char,scene,emotion,pub,prompt,seed,sz)
                    log(f"  [{i+1:03d}] ✅ {char}/{scene}/{emotion} | {sz}KB | id={bid}")
                    counts["ok"]+=1; ok=True; break
        except Exception as e: log(f"  [{i+1}] err{attempt+1}: {str(e)[:40]}")
        if attempt<2: time.sleep(5)
    if not ok:
        counts["fail"]+=1
        log(f"  [{i+1:03d}] ❌ {char}/{scene}/{emotion}")
    if i<len(batch_prompts)-1: time.sleep(DELAY)

log(f"\n  BATCH {BATCH}: {counts['ok']}/{len(batch_prompts)} OK | {counts['fail']} falhas")
log(f"  Total prompts disponíveis: {len(ALL_PROMPTS)} ({len(ALL_PROMPTS)//BATCH_SIZE} batches)")
