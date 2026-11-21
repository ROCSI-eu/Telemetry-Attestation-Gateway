#!/usr/bin/env python3
"""Author-only renderer for original TAG synthetic route/social graphics.

Requires Pillow only when re-authoring branded graphics on QA. The Cloudflare
build reads committed PNG/SVG/ICO assets and has no imaging dependency.
No external images, fonts, network calls or client/source telemetry are used.
"""
from __future__ import annotations
from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parent / "assets"
NAVY = (6, 22, 42)
CYAN = (105, 232, 239)
PALE = (235, 247, 255)
MUTED = (179, 205, 224)
FONT = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
BOLD = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")

def font(px: int, bold: bool = False):
    return ImageFont.truetype(str(BOLD if bold else FONT), px)

def glow(canvas, box, fill, radius=18, blur=18, strength=0.35):
    overlay = Image.new("RGBA", canvas.size)
    d=ImageDraw.Draw(overlay)
    d.rounded_rectangle(box, radius=radius, outline=fill+(int(255*strength),), width=3)
    canvas.alpha_composite(overlay.filter(ImageFilter.GaussianBlur(blur)))

def stroke_line(d, start, end, fill, width=3, dash=12, gap=10):
    x1,y1=start;x2,y2=end
    length=math.hypot(x2-x1,y2-y1)
    if not length:return
    t=0
    while t<length:
        a=t/length;b=min(t+dash,length)/length
        d.line((x1+(x2-x1)*a,y1+(y2-y1)*a,x1+(x2-x1)*b,y1+(y2-y1)*b),fill=fill,width=width)
        t+=dash+gap

def drone(draw, cx, cy, scale=1.0):
    def coords(seq):
        return [(int(cx+x*scale),int(cy+y*scale)) for x,y in seq]
    draw.ellipse((cx-47*scale,cy+34*scale,cx+47*scale,cy+51*scale),fill=(2,15,26,185))
    # Fixed-wing synthetic craft, not a live vehicle or physical flight track.
    draw.polygon(coords([(-94,-19),(-49,-28),(-19,-12),(0,-30),(19,-12),(49,-28),(94,-19),(61,-5),(19,8),(0,20),(-19,8),(-61,-5)]),fill=(42,157,185))
    draw.polygon(coords([(-94,-19),(-70,-31),(-14,-21),(0,-37),(14,-21),(70,-31),(94,-19),(35,-2),(0,8),(-35,-2)]),fill=(106,223,235))
    draw.polygon(coords([(-40,18),(-17,3),(-4,16),(-25,35)]),fill=(37,143,173))
    draw.polygon(coords([(40,18),(17,3),(4,16),(25,35)]),fill=(37,143,173))
    draw.polygon(coords([(-25,-15),(0,-39),(25,-15),(0,11)]),fill=(216,251,255))
    draw.polygon(coords([(-19,-16),(0,-34),(18,-16),(0,5)]),fill=(54,177,200))
    draw.polygon(coords([(-7,-15),(0,-23),(7,-15),(0,-7)]),fill=(174,252,250))
    draw.line(coords([(-93,-19),(-82,-22)]),fill=(206,255,255),width=max(2,int(scale*4)))
    draw.line(coords([(82,-22),(93,-19)]),fill=(206,255,255),width=max(2,int(scale*4)))

def base_image(width,height):
    im=Image.new("RGBA",(width,height))
    px=im.load()
    for y in range(height):
        for x in range(width):
            factor=max(0.,1.-math.hypot((x-width*.7)/(width*.9),(y-height*.5)/(height*1.35)))
            px[x,y]=(int(4+9*factor),int(18+36*factor),int(37+55*factor),255)
    return im

def draw_social(lang: str):
    W,H=1200,630
    canvas=base_image(W,H)
    d=ImageDraw.Draw(canvas,"RGBA")
    glow(canvas,(34,28,W-34,H-27),(63,214,234),radius=30,blur=20,strength=.55)
    d.rounded_rectangle((35,28,W-35,H-28),radius=29,outline=(65,183,215,220),width=2)
    # Grid and concentric rings only behind the synthetic-route illustration.
    for x in range(610,1150,54):
        d.line((x,125,x,535),fill=(26,78,106,255),width=1)
    for y in range(130,550,53):
        d.line((610,y,1144,y),fill=(68,160,193,18),width=1)
    for rad in [94,164,231]:
        d.ellipse((866-rad,325-rad,866+rad,325+rad),outline=(29,106,132,255),width=2)
    d.text((83,58),"ROCSI  /  TELEMETRY ATTESTATION GATEWAY",font=font(16,True),fill=(163,231,238))
    badge=("DEMO PUBLIC · REZULTATE PRECALCULATE" if lang=="ro" else
           "PUBLIC SHOWCASE · PRECOMPUTED ONLY")
    badgew=d.textbbox((0,0),badge,font=font(14,True))[2]
    bx=W-badgew-90
    d.rounded_rectangle((bx-14,51,W-67,85),radius=17,outline=(105,229,240,185),width=2,fill=(5,34,51,160))
    d.text((bx,59),badge,font=font(14,True),fill=(206,246,249))
    if lang=="ro":
        title=["Centru de comandă","și control"]
        subtitle=["Atestarea telemetriei","prin scenarii sintetice"]
        desc=["Vizualizare ilustrativă, reluare de scenarii","și rezultate de verificare offline","preînregistrate."]
        titlefont=font(43,True)
        titleY=139
        subY=296
        descY=401
    else:
        title=["Mission Control"]
        subtitle=["Observation-only telemetry","attestation concept"]
        desc=["Synthetic scenarios, deterministic replay,","and recorded offline verification."]
        titlefont=font(57,True)
        titleY=147
        subY=291
        descY=405
    for n,line in enumerate(title):
        d.text((84,titleY+n*59),line,font=titlefont,fill=PALE)
    d.rounded_rectangle((83,subY-1,89,subY+78),radius=3,fill=(106,237,241))
    for n,line in enumerate(subtitle):
        d.text((111,subY+n*41),line,font=font(28),fill=(228,244,253))
    for n,line in enumerate(desc):
        d.text((84,descY+n*30),line,font=font(18),fill=MUTED)
    # Route A--B--C with an illustrative aircraft and visible non-geographic path.
    points=[(640,461),(874,335),(1118,190)]
    for a,b in zip(points,points[1:]):
        d.line((*a,*b),fill=(13,85,114,255),width=8)
        stroke_line(d,a,b,(129,242,238,225),3,12,10)
    for n,(x,y) in enumerate(points):
        d.ellipse((x-7,y-7,x+7,y+7),fill=(154,255,243),outline=(8,57,81),width=3)
        d.text((x-11,y+16 if n==0 else y-37),chr(65+n),font=font(19,True),fill=PALE)
    drone(d,830,358,scale=.68)
    d.line((82,537,W-81,537),fill=(46,125,146,255),width=1)
    d.text((83,553),"tag.rocsi.eu",font=font(24,True),fill=PALE)
    footer=("SINTETIC · FĂRĂ TELEMETRIE SAU COMENZI LIVE" if lang=="ro"
            else "SYNTHETIC · NO LIVE TELEMETRY OR COMMANDS")
    width=d.textbbox((0,0),footer,font=font(12,True))[2]
    d.text((W-width-84,565),footer,font=font(12,True),fill=(121,209,222))
    file=ROOT/"og"/f"{lang}.png";file.parent.mkdir(parents=True,exist_ok=True)
    canvas.convert("RGB").save(file,optimize=True)
    assert file.stat().st_size<450000, ("Social image exceeds size budget",file.stat().st_size)
    print(file, file.stat().st_size)

SVG_ICON='''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="TAG — dronă ilustrativă și radar">
<rect width="64" height="64" rx="13" fill="#06172e"/>
<circle cx="32" cy="30" r="25" fill="none" stroke="#1ca6b6" stroke-width="2"/>
<circle cx="32" cy="30" r="15" fill="none" stroke="#176e89" stroke-width="1.4"/>
<path d="M32 4v7M32 49v7M5 30h8M51 30h8" stroke="#7df2e7" stroke-width="2" stroke-linecap="round"/>
<path d="M10 28L22 23L32 15L42 23L54 28L41 32L32 39L23 32Z" fill="#6ee1ec" stroke="#d0ffff" stroke-width="1.3" stroke-linejoin="round"/>
<path d="M23 32L16 41L24 37L32 40L40 37L48 41L41 32" fill="#228da8"/>
<path d="M25 29L32 20L39 29L32 35Z" fill="#c6ffff"/>
<circle cx="32" cy="28" r="2" fill="#1f8798"/>
</svg>
'''

def draw_icon():
    ROOT.mkdir(parents=True,exist_ok=True)
    (ROOT/"favicon.svg").write_text(SVG_ICON,encoding="utf-8")
    def icon_at(size):
        im=Image.new("RGB",(size,size),NAVY)
        d=ImageDraw.Draw(im)
        scale=size/128
        def sc(v):return round(v*scale)
        d.rounded_rectangle((0,0,size-1,size-1),radius=sc(24),fill=(5,24,46),outline=(32,124,153),width=max(1,sc(3)))
        for r,col in [(50,(31,176,196)),(35,(21,91,122))]:
            d.ellipse((sc(64-r),sc(61-r),sc(64+r),sc(61+r)),outline=col,width=max(1,sc(3)))
        for a,b in [((64,6),(64,20)),((64,104),(64,119)),((8,61),(22,61)),((106,61),(120,61))]:
            d.line((sc(a[0]),sc(a[1]),sc(b[0]),sc(b[1])),fill=(116,232,230),width=max(1,sc(3)))
        cx,cy=64,59
        def ps(p):return [(sc(cx+x),sc(cy+y)) for x,y in p]
        d.polygon(ps([(-43,-6),(-22,-14),(0,-34),(22,-14),(43,-6),(25,4),(0,23),(-25,4)]),fill=(103,224,231))
        d.polygon(ps([(-25,4),(-32,17),(-16,8),(0,25),(16,8),(32,17),(25,4)]),fill=(32,124,151))
        d.polygon(ps([(-18,-4),(0,-24),(18,-4),(0,12)]),fill=(207,252,255))
        d.polygon(ps([(-11,-3),(0,-17),(11,-3),(0,8)]),fill=(46,157,186))
        return im
    icon_at(180).save(ROOT/"apple-touch-icon.png",optimize=True)
    icon_at(256).save(ROOT/"favicon.ico",format="ICO",sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)])
    print("icon files",[(x.name,x.stat().st_size) for x in ROOT.iterdir() if x.is_file()])

if __name__=="__main__":
    draw_icon()  # Social OG PNGs are owned by social_og_builder.mjs
