"""Deterministic editorial illustration. No dependencies or network."""
import os, struct, zlib, math
from pathlib import Path
W=H=1024
C={'ink':'182c38','paper':'f3ead7','light':'fff8e9','red':'bd4c42','teal':'167e81','gold':'dca74d','blue':'365d83','grey':'567079','white':'ffffff','dark':'102530'}
def color(v): return bytes.fromhex(C.get(v,v))
pix=bytearray(color('paper')*(W*H))
def rect(x,y,w,h,c):
    a=max(0,int(x)); b=min(W,int(x+w)); t=max(0,int(y)); u=min(H,int(y+h))
    if b<=a or u<=t:return
    row=color(c)*(b-a)
    for j in range(t,u):pix[(j*W+a)*3:(j*W+b)*3]=row
def circle(x,y,r,c):
    for j in range(-r,r+1):
        dx=math.isqrt(r*r-j*j);rect(x-dx,y+j,dx*2+1,1,c)
def line(x,y,X,Y,c,w=4):
    n=max(abs(X-x),abs(Y-y),1)
    for i in range(n+1):circle(round(x+(X-x)*i/n),round(y+(Y-y)*i/n),w,c)
# Compact original 5x7 lettering, hex row masks.
font=dict(zip('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+/-:', '''0E11111F111111 1E11111E11111E 0F10101010100F 1E11111111111E 1F10101E10101F 1F10101E101010 0F10101711110F 1111111F111111 0E04040404040E 0702020212120C 11121418141211 1010101010101F 111B1515111111 11191513111111 0E11111111110E 1E11111E101010 0E11111115120D 1E11111E141211 0F10100E01011E 1F040404040404 1111111111110E 11111111110A04 11111115151B11 11110A040A1111 11110A04040404 1F01020408101F 0E11131519110E 040C040404040E 0E11010204081F 1E01010E01011E 02060A121F0202 1F10101E01011E 0E10101E11110E 1F010204080808 0E11110E11110E 0E11110F01010E 0004041F040400 01020404081010 0000001F000000 00040000040000'''.split()))
def txt(x,y,s,k=4,c='ink'):
    for ch in s.upper():
        glyph=font.get(ch)
        if glyph:
            for j in range(7):
                bits=int(glyph[2*j:2*j+2],16)
                for i in range(5):
                    if bits&(16>>i):rect(x+i*k,y+j*k,k,k,c)
        x+=6*k

def icon(n,x,y,accent):
    # A compact circular editorial symbol, always a schematic illustration.
    circle(x,y,65,accent); circle(x,y,53,'dark')
    def r(a,b,w,h,c='light'):rect(x+a,y+b,w,h,c)
    def l(a,b,d,e,c='light',w=3):line(x+a,y+b,x+d,y+e,c,w)
    def o(a,b,z,c='light'):circle(x+a,y+b,z,c)
    if n==0: # satellite communications
        r(-15,-13,30,26);r(-46,-18,26,36,'blue');r(20,-18,26,36,'blue');l(-20,0,-15,0);l(15,0,20,0);l(-38,-42,38,42,'red',5)
    elif n==1: # humanitarian shelter, rainfall
        l(-39,20,0,-27);l(0,-27,39,20);l(-39,20,39,20);l(0,-27,0,20);r(-45,27,90,6,'teal')
        for a,b in [(-36,-40),(-12,-48),(18,-38),(40,-30)]:l(a,b,a-5,b+10,'blue',2)
    elif n==2: # globe and finance
        o(-10,0,34,'teal');l(-43,0,23,0);l(-10,-32,-10,31);l(-37,-17,17,-17);l(-37,17,17,17);o(25,23,21,'gold');txt(x+14,y+10,'+',4,'dark')
    elif n==3: # tanker and narrow strait
        r(-38,-10,76,20);r(-25,-24,42,15,'gold');r(20,-32,14,21);l(-43,15,43,15,'teal');l(-40,26,40,26,'teal');l(-44,-39,-28,-27,'red');l(40,-39,29,-29,'red')
    elif n==4: # global communications outage
        r(-39,-27,78,51);r(-34,-22,68,38,'blue');l(-32,-18,0,5);l(0,5,32,-18);r(-14,29,28,6);l(-39,-42,40,42,'red',5)
    elif n==5: # India bus collision
        r(-43,-15,51,30,'gold');r(-37,-11,10,10,'dark');r(-22,-11,10,10,'dark');r(-7,-11,10,10,'dark');r(15,-19,28,34);o(-32,19,7);o(-3,19,7);o(24,19,7);o(38,19,7);l(6,-36,14,-24,'red');l(17,-37,13,-25,'red')
    elif n==6: # construction collapse
        for i in range(4):r(-34,25-i*14,54,5);r(-30,15-i*14,5,10);r(10,15-i*14,5,10)
        l(-32,-37,16,-23,'red',5);l(26,6,41,20,'gold',4);l(26,21,42,29,'gold',4)
    else: # rescue vessel and life ring
        r(-42,-5,75,18);r(-29,-24,45,18);l(-44,21,40,21,'teal',4);l(-40,31,43,31,'teal',3);o(27,-20,20,'red');o(27,-20,10,'dark');l(27,-40,27,-31);l(27,-9,27,0)

cards=[('UKRAINE / WAR',['STARSHIELD','CURBS HIT','FRONT LINE'],'blue'),('GAZA / AID',['UN URGES','WINTER AID','FOR GAZA'],'red'),('TURKEY / COP31',['CLIMATE','FINANCE','IN FOCUS'],'teal'),('GULF / SECURITY',['UN DEBATES','HORMUZ','SHIP THREATS'],'blue'),('WORLD / TECH',['MICROSOFT','GLOBAL','OUTAGE'],'teal'),('INDIA / ASSAM',['BUS CRASH','AT LEAST','24 KILLED'],'red'),('KENYA / NAIROBI',['BUILDING','COLLAPSE','6 KILLED'],'gold'),('USA / MISSISSIPPI',['TANKER HITS','RIVER CRUISE','ALL RESCUED'],'blue')]
rect(0,0,1024,142,'ink');rect(0,138,1024,4,'gold');txt(35,20,'FRIDAY / 13 NOV 2026',4,'gold');txt(35,67,'THE WORLD TODAY',9,'light')
for n,(region,headline,accent) in enumerate(cards):
    x=28+(n%2)*490;y=160+(n//2)*205
    rect(x,y,478,193,'light');rect(x,y,7,193,accent);rect(x+14,y+12,450,32,accent)
    txt(x+24,y+18,region,3,'dark' if accent=='gold' else 'white')
    for i,t in enumerate(headline):txt(x+22,y+60+i*40,t,4,'ink')
    icon(n,x+399,y+120,accent)
rect(0,985,1024,39,'ink');txt(28,996,'ILLUSTRATED NEWS BRIEF / AP - REUTERS - UN',3,'light')
def chunk(t,data):return struct.pack('>I',len(data))+t+data+struct.pack('>I',zlib.crc32(t+data)&0xffffffff)
raw=b''.join(b'\0'+pix[i:i+W*3] for i in range(0,len(pix),W*3))
image=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',W,H,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(raw,9))+chunk(b'IEND',b'')
assert len(image)<=1048576
out=Path(os.environ.get('MAKEFUN_OUTPUT_DIR','/output'));out.mkdir(parents=True,exist_ok=True);(out/'entry.png').write_bytes(image)
