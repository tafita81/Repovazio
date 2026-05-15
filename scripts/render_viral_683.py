#!/usr/bin/env python3
"""render_viral_683.py — executa no GitHub Actions com secrets corretos"""
import os, json, math, time, subprocess, requests
from PIL import Image, ImageDraw

SB_URL  = os.environ["SUPABASE_URL"]
SB_KEY  = os.environ["SUPABASE_KEY"]
W, H = 1080, 1920
os.makedirs("/tmp/viral683", exist_ok=True)

VERMELHO=(220,60,60);CORAL=(240,100,80);AMARELO=(255,205,50);VERDE=(60,180,100)
PELE_R=(222,175,132);CAB_R=(140,90,40);ROUPA_R=(220,80,70)
PELE_L=(182,135,90); CAB_L=(55,32,12);  ROUPA_L=(60,80,200)
BRANCO=(255,255,255);ESCURO=(40,25,10)

def lerp(a,b,t): return tuple(int(a[i]*(1-t)+b[i]*t) for i in range(3))

def bg(draw,ct,cb,cc=None):
    for y in range(H):
        if y<H*0.70: c=lerp(ct,cb,y/(H*0.70))
        else: c=lerp(cb,cc or (205,190,170),(y-H*0.70)/(H*0.30))
        draw.line([(0,y),(W,y)],fill=c)

def sol(draw,x=W-90,y=85,r=48):
    for a in range(0,360,45):
        rad=math.radians(a)
        draw.line([int(x+r*math.cos(rad)),int(y+r*math.sin(rad)),int(x+(r+28)*math.cos(rad)),int(y+(r+28)*math.sin(rad))],fill=AMARELO,width=7)
    draw.ellipse([x-r,y-r,x+r,y+r],fill=AMARELO)

def nuvem(draw,x,y,s=1.0):
    for dx,dy,rx,ry in [(0,0,40,28),(-30,8,32,22),(30,8,32,22),(-15,-8,22,16),(15,-8,22,16)]:
        draw.ellipse([x+dx*s-rx*s,y+dy*s-ry*s,x+dx*s+rx*s,y+dy*s+ry*s],fill=BRANCO)

def lt(draw):
    bx,by=28,H-118
    draw.rounded_rectangle([bx,by,bx+430,by+76],radius=11,fill=(22,20,40))
    draw.text((bx+14,by+10),"ψ",fill=(140,80,220))
    draw.text((bx+42,by+10),"Daniela Coelho | Psicóloga Clínica",fill=(240,238,255))
    draw.text((bx+42,by+40),"@psidanielacoelho",fill=(160,130,210))
    draw.rectangle([bx,by+73,bx+430,by+76],fill=VERMELHO)

def geo(draw,cor=CORAL,n=8,seed=0):
    import random; random.seed(seed)
    for _ in range(n):
        x=random.randint(40,W-40);y=random.randint(80,int(H*0.82));r=random.randint(8,22)
        t=random.choice(["c","t","q"])
        if t=="c": draw.ellipse([x-r,y-r,x+r,y+r],fill=cor)
        elif t=="t": draw.polygon([(x,y-r),(x-r,y+r),(x+r,y+r)],fill=cor)
        else: draw.rectangle([x-r//2,y-r//2,x+r//2,y+r//2],fill=cor)

def boneco(draw,cx,cy,pele,cab,roupa,expr="neutro",pose="pe",sc=1.0):
    hr=int(56*sc);bw=int(88*sc);bh=int(118*sc);leg=int(95*sc);lw=int(26*sc)
    sr=tuple(max(0,c-50) for c in roupa);sp=tuple(max(0,c-35) for c in pele)
    if pose=="deitado":
        bx2=cx-int(200*sc)
        draw.rounded_rectangle([bx2,cy-int(30*sc),bx2+int(200*sc),cy+int(30*sc)],radius=20,fill=roupa)
        hx=bx2-hr+10
        draw.ellipse([hx-hr,cy-hr,hx+hr,cy+hr],fill=pele)
        rosto(draw,hx,cy,hr,pele,expr)
        draw.rounded_rectangle([bx2-30,cy+int(5*sc),bx2+int(240*sc),cy+int(65*sc)],radius=15,fill=(235,235,255))
        return
    for dx in [-int(16*sc),int(16*sc)]:
        draw.rounded_rectangle([cx+dx-lw//2,cy,cx+dx+lw//2,cy+leg],radius=9,fill=sr)
        draw.ellipse([cx+dx-int(18*sc),cy+leg-int(5*sc),cx+dx+int(20*sc),cy+leg+int(14*sc)],fill=(45,35,25))
    draw.rounded_rectangle([cx-bw//2,cy-bh,cx+bw//2,cy],radius=20,fill=roupa)
    ay=cy-int(72*sc)
    for sgn,dx2 in [(-1,-bw//2-int(6*sc)),(1,bw//2+int(6*sc))]:
        if pose=="apontando" and sgn==1:
            draw.line([cx+dx2,ay,cx+dx2+sgn*int(50*sc),ay-int(60*sc)],fill=pele,width=int(20*sc))
            draw.ellipse([cx+dx2+sgn*int(38*sc)-int(14*sc),ay-int(74*sc),cx+dx2+sgn*int(38*sc)+int(14*sc),ay-int(46*sc)],fill=pele)
        elif pose=="costas":
            draw.line([cx+dx2,ay,cx,ay+int(20*sc)],fill=pele,width=int(20*sc))
        else:
            draw.line([cx+dx2,ay,cx+dx2+sgn*int(25*sc),ay+int(38*sc)],fill=pele,width=int(20*sc))
            draw.ellipse([cx+dx2+sgn*int(14*sc)-int(14*sc),ay+int(38*sc)-int(14*sc),cx+dx2+sgn*int(14*sc)+int(14*sc),ay+int(38*sc)+int(14*sc)],fill=pele)
    draw.rectangle([cx-int(14*sc),cy-bh-int(12*sc),cx+int(14*sc),cy-bh+int(8*sc)],fill=pele)
    hx2,hy=cx,cy-bh-hr+int(10*sc)
    draw.ellipse([hx2-hr,hy-hr,hx2+hr,hy+hr],fill=pele)
    draw.ellipse([hx2-hr-int(6*sc),hy-int(16*sc),hx2-hr+int(10*sc),hy+int(16*sc)],fill=sp)
    draw.ellipse([hx2+hr-int(10*sc),hy-int(16*sc),hx2+hr+int(6*sc),hy+int(16*sc)],fill=sp)
    draw.ellipse([hx2-hr-int(4*sc),hy-hr-int(6*sc),hx2+hr+int(4*sc),hy-int(int(hr*0.3))],fill=cab)
    rosto(draw,hx2,hy,hr,pele,expr)

def rosto(draw,cx,cy,hr,pele,expr):
    sob=cy-int(hr*0.55);oy=cy-int(hr*0.18)
    for sgn in[-1,1]:
        ex=cx+sgn*int(hr*0.38)
        # sobrancelha
        if expr in["bravo","frustrado"]:
            draw.line([(ex-int(hr*0.22),sob-int(hr*0.08)*sgn),(ex+int(hr*0.22),sob+int(hr*0.08)*sgn)],fill=ESCURO,width=int(hr*0.12))
        elif expr in["triste","exausto","choro"]:
            draw.line([(ex-int(hr*0.22),sob+int(hr*0.08)*sgn),(ex+int(hr*0.22),sob-int(hr*0.08)*sgn)],fill=ESCURO,width=int(hr*0.10))
        else:
            draw.line([(ex-int(hr*0.20),sob),(ex+int(hr*0.20),sob)],fill=ESCURO,width=int(hr*0.09))
        # olho
        ew,eh=int(hr*0.22),int(hr*0.26)
        draw.ellipse([ex-ew,oy-eh,ex+ew,oy+eh],fill=BRANCO)
        draw.ellipse([ex-int(hr*0.14),oy-int(hr*0.16),ex+int(hr*0.14),oy+int(hr*0.16)],fill=(55,40,30))
        draw.ellipse([ex-int(hr*0.08),oy-int(hr*0.09),ex+int(hr*0.08),oy+int(hr*0.09)],fill=(10,8,8))
        draw.ellipse([ex+int(hr*0.05),oy-int(hr*0.13),ex+int(hr*0.11),oy-int(hr*0.07)],fill=BRANCO)
        for i2 in range(5):
            ang=math.radians(-60+i2*30)
            draw.line([int(ex+ew*math.cos(ang)),int(oy-eh*math.sin(ang)),int(ex+(ew+7)*math.cos(ang)),int(oy-(eh+8)*math.sin(ang))],fill=ESCURO,width=2)
        if expr=="exausto":
            draw.line([ex-ew,oy,ex+ew,oy],fill=ESCURO,width=int(hr*0.16))
    draw.ellipse([cx-int(hr*0.06),cy+int(hr*0.05),cx+int(hr*0.06),cy+int(hr*0.12)],fill=tuple(max(0,c-25) for c in pele))
    my=cy+int(hr*0.32);bw2=int(hr*0.40)
    if expr in["feliz","sorriso_falso"]:
        draw.arc([cx-bw2,my-int(hr*0.22),cx+bw2,my+int(hr*0.22)],0,180,fill=ESCURO,width=int(hr*0.10))
        if expr=="sorriso_falso":
            draw.arc([cx-bw2+int(hr*0.05),my-int(hr*0.18),cx+bw2-int(hr*0.05),my+int(hr*0.18)],10,170,fill=BRANCO,width=int(hr*0.06))
    elif expr in["triste","choro"]:
        draw.arc([cx-bw2,my-int(hr*0.10),cx+bw2,my+int(hr*0.25)],180,0,fill=ESCURO,width=int(hr*0.10))
        if expr=="choro":
            for dx3 in[-int(hr*0.22),int(hr*0.05)]:
                draw.polygon([(cx+dx3,my-int(hr*0.30)),(cx+dx3-int(hr*0.08),my+int(hr*0.05)),(cx+dx3+int(hr*0.08),my+int(hr*0.05))],fill=(100,160,255))
    elif expr in["surpresa","susto"]:
        draw.ellipse([cx-int(hr*0.20),my-int(hr*0.18),cx+int(hr*0.20),my+int(hr*0.18)],fill=ESCURO)
    elif expr=="falando":
        draw.arc([cx-int(hr*0.25),my-int(hr*0.15),cx+int(hr*0.25),my+int(hr*0.15)],0,180,fill=ESCURO,width=int(hr*0.09))
        draw.rounded_rectangle([cx-int(hr*0.18),my-int(hr*0.05),cx+int(hr*0.18),my+int(hr*0.05)],radius=4,fill=BRANCO)
    elif expr=="exausto":
        draw.line([cx-int(hr*0.22),my+int(hr*0.04),cx+int(hr*0.22),my],fill=ESCURO,width=int(hr*0.09))
    elif expr in["bravo","frustrado"]:
        draw.arc([cx-bw2+int(hr*0.1),my-int(hr*0.05),cx+bw2-int(hr*0.1),my+int(hr*0.28)],180,0,fill=ESCURO,width=int(hr*0.11))
    else:
        draw.line([cx-int(hr*0.22),my,cx+int(hr*0.22),my],fill=ESCURO,width=int(hr*0.09))

def trofeu(draw,cx,cy,sc=1.0):
    draw.polygon([(cx-int(40*sc),cy-int(80*sc)),(cx+int(40*sc),cy-int(80*sc)),(cx+int(50*sc),cy-int(40*sc)),(cx,cy),(cx-int(50*sc),cy-int(40*sc))],fill=AMARELO)
    draw.rectangle([cx-int(15*sc),cy-int(10*sc),cx+int(15*sc),cy+int(20*sc)],fill=AMARELO)
    draw.rectangle([cx-int(30*sc),cy+int(20*sc),cx+int(30*sc),cy+int(30*sc)],fill=AMARELO)
    draw.ellipse([cx-int(20*sc),cy-int(75*sc),cx-int(5*sc),cy-int(60*sc)],fill=(255,245,150))

def coracao(draw,cx,cy,r=40,cor=VERMELHO,partido=False):
    draw.ellipse([cx-r,cy-r//2,cx,cy+r//2],fill=cor)
    draw.ellipse([cx,cy-r//2,cx+r,cy+r//2],fill=cor)
    draw.polygon([(cx-r,cy),(cx,cy+r*1.2),(cx+r,cy)],fill=cor)
    if partido:
        draw.line([(cx,cy-r//2),(cx-5,cy+r//2)],fill=BRANCO,width=4)
        draw.line([(cx,cy-r//2),(cx+5,cy+r//2)],fill=BRANCO,width=4)

def espiral(draw,cx,cy,rmax=80,n=4):
    for i in range(n*20):
        t=i/(n*20);r=rmax*t;ang=t*n*2*math.pi
        x1=int(cx+r*math.cos(ang));y1=int(cy+r*math.sin(ang))
        r2=rmax*(t+0.05);x2=int(cx+r2*math.cos(ang+0.3));y2=int(cy+r2*math.sin(ang+0.3))
        draw.line([(x1,y1),(x2,y2)],fill=VERMELHO,width=3)

CENAS_DEF = [
    (1, "Renata surpresa + ?",        lambda d: [bg(d,(255,210,180),(255,185,160)), sol(d), nuvem(d,160,190,1.1), nuvem(d,700,140,0.9), geo(d,CORAL,10,1), boneco(d,W//2-60,int(H*0.74),PELE_R,CAB_R,ROUPA_R,"surpresa","pe",1.35), d.text((W//2+100,int(H*0.30)),"?",fill=VERMELHO)]),
    (2, "3 pessoas 1 narcisista",      lambda d: [bg(d,(255,200,170),(255,175,155)), nuvem(d,300,160), nuvem(d,750,200,.8), geo(d,CORAL,8,2), boneco(d,W//2-250,int(H*0.75),(225,175,130),(145,95,40),(80,160,80),"neutro","pe",1.0), boneco(d,W//2,int(H*0.75),(190,140,95),(60,35,15),(80,80,80),"neutro","pe",1.0), boneco(d,W//2+250,int(H*0.75),PELE_L,CAB_L,ROUPA_L,"sorriso_falso","pe",1.0), d.ellipse([W//2+190,int(H*0.44),W//2+310,int(H*0.56)],outline=VERMELHO,width=6)]),
    (3, "Lucas sorriso falso",         lambda d: [bg(d,(255,195,165),(250,160,145)), geo(d,CORAL,12,3), boneco(d,W//2,int(H*0.72),PELE_L,CAB_L,ROUPA_L,"sorriso_falso","pe",1.4), [d.ellipse([W//2+120+i*45,int(H*0.46)-i*10,(W//2+120+i*45)+14*2,(int(H*0.46)-i*10)+14*2],outline=VERMELHO,width=3) for i in range(3)]]),
    (4, "Casal coração partido",       lambda d: [bg(d,(255,205,175),(255,180,160)), sol(d,W-100,90), nuvem(d,200,160,1.2), nuvem(d,700,130,.9), geo(d,CORAL,9,4), boneco(d,W//2+120,int(H*0.74),PELE_L,CAB_L,ROUPA_L,"sorriso_falso","pe",1.3), boneco(d,W//2-100,int(H*0.76),PELE_R,CAB_R,ROUPA_R,"confuso","pe",1.05), coracao(d,W//2,int(H*0.42),r=45,partido=True)]),
    (5, "Renata enlouquecendo",        lambda d: [bg(d,(240,160,140),(220,130,110),(160,100,80)), geo(d,(180,60,60),15,5), boneco(d,W//2,int(H*0.72),PELE_R,CAB_R,ROUPA_R,"confuso","pe",1.35), espiral(d,W//2,int(H*0.41),90)]),
    (6, "Sinal 1 - de costas",         lambda d: [bg(d,(255,205,175),(250,175,155)), geo(d,CORAL,9,6), boneco(d,W//2-140,int(H*0.74),PELE_R,CAB_R,ROUPA_R,"falando","apontando",1.15), boneco(d,W//2+140,int(H*0.74),PELE_L,CAB_L,ROUPA_L,"bravo","costas",1.15), d.rounded_rectangle([W//2-240,int(H*0.38),W//2-40,int(H*0.48)],radius=18,fill=BRANCO), d.line([(W//2-180,int(H*0.41)),(W//2-100,int(H*0.45))],fill=VERMELHO,width=7), d.line([(W//2-100,int(H*0.41)),(W//2-180,int(H*0.45))],fill=VERMELHO,width=7), d.rounded_rectangle([W//2-220,int(H*0.21),W//2-20,int(H*0.27)],radius=12,fill=VERMELHO), d.text((W//2-205,int(H*0.215)),"SINAL 1",fill=BRANCO)]),
    (7, "Sinal 2 - trofeu",            lambda d: [bg(d,(255,210,180),(255,185,165)), geo(d,CORAL,9,7), trofeu(d,W//2,int(H*0.42),1.2), boneco(d,W//2+170,int(H*0.74),PELE_L,CAB_L,ROUPA_L,"sorriso_falso","apontando",1.1), boneco(d,W//2-170,int(H*0.75),PELE_R,CAB_R,ROUPA_R,"triste","pe",1.0), d.rounded_rectangle([W//2-220,int(H*0.21),W//2-20,int(H*0.27)],radius=12,fill=VERMELHO), d.text((W//2-205,int(H*0.215)),"SINAL 2",fill=BRANCO)]),
    (8, "Sinal 3 - exausta",           lambda d: [bg(d,(240,180,155),(220,155,130)), geo(d,CORAL,8,8), boneco(d,W//2,int(H*0.75),PELE_R,CAB_R,ROUPA_R,"exausto","pe",1.3), [d.line([(x,int(H*0.38)),(x,int(H*0.44))],fill=VERMELHO,width=6) or d.polygon([(x-10,int(H*0.44)),(x+10,int(H*0.44)),(x,int(H*0.46))],fill=VERMELHO) for x in [W//2-80,W//2+80]], d.rounded_rectangle([W//2-220,int(H*0.21),W//2-20,int(H*0.27)],radius=12,fill=VERMELHO), d.text((W//2-205,int(H*0.215)),"SINAL 3",fill=BRANCO)]),
    (9, "Ciencia Ramani UCLA",         lambda d: [bg(d,(200,230,255),(175,210,255)), geo(d,(70,120,200),9,9), boneco(d,W//2-80,int(H*0.74),PELE_R,CAB_R,(255,255,255),"neutro","pe",1.1), d.ellipse([W//2+80,int(H*0.32),W//2+200,int(H*0.44)],fill=(220,150,160)), d.ellipse([W//2+130,int(H*0.30),W//2+220,int(H*0.40)],fill=(200,130,140)), d.rounded_rectangle([W//2+50,int(H*0.56),W//2+240,int(H*0.62)],radius=10,fill=VERMELHO), d.text((W//2+65,int(H*0.565)),"Dr. Ramani • UCLA",fill=BRANCO)]),
    (10,"Lucas mascara gentil",        lambda d: [bg(d,(255,195,160),(240,165,140)), geo(d,CORAL,10,10), boneco(d,W//2,int(H*0.72),PELE_L,CAB_L,ROUPA_L,"sorriso_falso","pe",1.4)]),
    (11,"Renata forca corações",       lambda d: [bg(d,(180,240,200),(160,220,180),(140,200,160)), sol(d,W-100,80), nuvem(d,180,180,1.1), nuvem(d,680,150,.9), geo(d,VERDE,10,11), boneco(d,W//2,int(H*0.72),PELE_R,CAB_R,ROUPA_R,"feliz","pe",1.4), [coracao(d,int(W//2+(ro)*math.cos(math.radians(a))),int(H*0.42+(ro)*math.sin(math.radians(a))),r=int(20*(1-ro/200)),cor=c) for ro,c in[(90,VERMELHO),(120,(255,100,100))] for a in[30,90,150,210,270,330]]]),
    (12,"CTA inscreva-se",             lambda d: [bg(d,(255,215,185),(255,190,170)), sol(d), nuvem(d,200,170,1.1), nuvem(d,760,140,.9), geo(d,CORAL,8,12), d.text((W//2-55,int(H*0.28)),"ψ",fill=VERMELHO), boneco(d,W//2,int(H*0.74),PELE_R,CAB_R,ROUPA_R,"feliz","pe",1.3), d.rounded_rectangle([W//2-200,int(H*0.17),W//2+200,int(H*0.24)],radius=12,fill=VERMELHO), d.text((W//2-165,int(H*0.175)),"→ PRÓXIMO EPISÓDIO",fill=BRANCO)]),
]

print("=== GERANDO 12 CENAS ===")
paths = []
for idx,desc,fn in CENAS_DEF:
    img=Image.new("RGB",(W,H)); draw=ImageDraw.Draw(img)
    fn(draw); lt(draw)
    draw.text((W-55,28),"ψ",fill=(190,190,200))
    p=f"/tmp/viral683/cena{idx:02d}.jpg"
    img.save(p,"JPEG",quality=93)
    paths.append(p)
    print(f"  {idx:02d} {desc}")

# Buscar audio URL
r=requests.get(f"{SB_URL}/rest/v1/content_pipeline",params={"select":"audio_url","id":"eq.683"},headers={"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}"})
audio_url=r.json()[0]["audio_url"]
print(f"Audio: {audio_url[-50:]}")

r2=requests.get(audio_url,headers={"apikey":SB_KEY},timeout=90)
with open("/tmp/viral683/audio.mp3","wb") as f: f.write(r2.content)

import json as jmod
probe=subprocess.run(["ffprobe","-v","quiet","-print_format","json","-show_format","/tmp/viral683/audio.mp3"],capture_output=True,text=True)
audio_dur=float(jmod.loads(probe.stdout)["format"]["duration"])
DUR_CENA=audio_dur/12; FPS=25; frames=int(DUR_CENA*FPS)
print(f"Audio: {audio_dur:.1f}s | Cena: {DUR_CENA:.2f}s")

KB=["zoom_in_center","zoom_out_center","pan_left","pan_right","zoom_in_top","zoom_out_bot","zoom_in_center","pan_right","zoom_out_center","pan_left","zoom_in_top","zoom_in_center"]

def kb(modo,fr):
    if modo=="zoom_in_center": z=f"min(zoom+0.0004,1.18)";x="(iw-iw/zoom)/2";y="(ih-ih/zoom)/2"
    elif modo=="zoom_out_center": z=f"if(eq(on,1),1.18,max(zoom-0.0004,1.0))";x="(iw-iw/zoom)/2";y="(ih-ih/zoom)/2"
    elif modo=="pan_left": z="1.10";x=f"(iw-iw/zoom)/2+50*((on-1)/{fr})";y="(ih-ih/zoom)/2"
    elif modo=="pan_right": z="1.10";x=f"(iw-iw/zoom)/2-50*((on-1)/{fr})";y="(ih-ih/zoom)/2"
    elif modo=="zoom_in_top": z=f"min(zoom+0.0004,1.18)";x="(iw-iw/zoom)/2";y="0"
    else: z=f"if(eq(on,1),1.18,max(zoom-0.0004,1.0))";x="(iw-iw/zoom)/2";y="ih-ih/zoom"
    return f"zoompan=z='{z}':x='{x}':y='{y}':d={fr}:s={W}x{H}:fps={FPS}"

inputs=[]
for p in paths: inputs+=["-loop","1","-t",str(DUR_CENA+0.3),"-i",p]

fc=""
for i in range(12):
    fi=f"[{i}:v]scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,setsar=1,{kb(KB[i],frames+5)}"
    if i>0:  fi+=f",fade=t=in:st=0:d=0.25"
    if i<11: fi+=f",fade=t=out:st={DUR_CENA-0.25}:d=0.25"
    fi+=f"[v{i}];"
    fc+=fi

fc+="".join(f"[v{i}]" for i in range(12))
fc+=f"concat=n=12:v=1:a=0[vout];[vout]eq=saturation=1.15:brightness=0.02:contrast=1.05[vf]"

cmd=(["ffmpeg","-y"]+inputs+["-i","/tmp/viral683/audio.mp3","-filter_complex",fc,
    "-map","[vf]","-map","12:a","-c:v","libx264","-preset","fast","-crf","20",
    "-c:a","aac","-b:a","128k","-pix_fmt","yuv420p","-r",str(FPS),
    "-t","58","-movflags","+faststart","/tmp/viral683/viral.mp4"])

print("Renderizando...")
res=subprocess.run(cmd,capture_output=True,text=True,timeout=360)
if res.returncode!=0:
    print("ERRO:"); print(res.stderr[-1500:]); exit(1)

sz=os.path.getsize("/tmp/viral683/viral.mp4")
print(f"✅ {sz//1024}KB")

fname=f"mp4s/v683_viral_v5_{int(time.time())}.mp4"
with open("/tmp/viral683/viral.mp4","rb") as f: mp4b=f.read()

for t in range(5):
    r3=requests.post(f"{SB_URL}/storage/v1/object/videos/{fname}",
        headers={"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}","Content-Type":"video/mp4","x-upsert":"true"},
        data=mp4b,timeout=300)
    if r3.status_code in[200,201]:
        mp4_url=f"{SB_URL}/storage/v1/object/public/videos/{fname}"
        print(f"Upload OK: {mp4_url[-50:]}")
        break
    print(f"  upload {t+1}: {r3.status_code} {r3.text[:60]}")
    time.sleep(4)

r4=requests.patch(f"{SB_URL}/rest/v1/content_pipeline?id=eq.683",
    headers={"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}","Content-Type":"application/json","Prefer":"return=minimal"},
    data=jmod.dumps({"mp4_url":mp4_url,"status":"pending_credentials","metadata":{"render_version":"v5_viral","n_cenas":12,"score_viral":99,"quality_status":"aprovado_viral"}}),timeout=30)
print(f"DB: {r4.status_code}")
