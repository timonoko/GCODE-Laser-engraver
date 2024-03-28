#! /usr/bin/python3
from PIL import Image, ImageFont, ImageDraw, ImageOps  
import time,sys,math,os,datetime

os.system('killall display')

IMG=Image.new(mode="RGB",size=(5000,5000),color=(255,255,200))

def parsee(s):
    i=0
    tulos={}
    number=""
    prevalfa="kakka"
    while i<len(s):
        if ord(s[i]) in range(ord('0'),ord('9')+1) or s[i]=='.':
            number+=s[i]
        else:
            if prevalfa != "kakka" and number != "":
                tulos.update({prevalfa:eval(number)})
                number=""
            if ord(s[i]) in range(ord('A'),ord('Z')+1):
                prevalfa=s[i]
        i+=1
    return tulos

MAX_X=0
MAX_Y=0
PREV_X=0
PREV_Y=0
PEN_DOWN=False

def mydraw(x1,y1,x2,y2):
    if abs(x2-x1)>abs(y2-y1):
        if x1>x2:
            x1,x2=x2,x1
            y1,y2=y2,y1
        for x in range(x1,x2):
            IMG.putpixel((x,int(y1+(x-x1)*((y2-y1)/(x2-x1)))),(0,0,0))
    else:
        if y1>y2:
            x1,x2=x2,x1
            y1,y2=y2,y1
        for y in range(y1,y2):
            IMG.putpixel((int(x1+(y-y1)*((x2-x1)/(y2-y1))),y),(0,0,0))
    IMG.putpixel((x2,y2),(0,0,0))

def Move2(s):
    global IMG,MAX_X,MAX_Y,PREV_X,PREV_Y
    x=int(10*s['X'])
    y=int(10*s['Y'])
    if x>MAX_X: MAX_X=x
    if y>MAX_Y: MAX_Y=y
    if PEN_DOWN:
        mydraw(PREV_X,PREV_Y,x,y)
    PREV_X=x
    PREV_Y=y

try:   F=open(sys.argv[1],'r')
except: F=open('gcode.gcode','r')

k=F.readline()
while k:
    k=F.readline()
    s=parsee(k)
    if 'G' in s:
        if s['G']==0:
            if 'X' in s: Move2(s) 
        elif s['G']==1:
            if 'X' in s: Move2(s) 
            if 'S' in s: pass #print('power',s['S'])
            if 'F' in s: pass #print('Speed',s['F'])
        elif s['G']==4:
            time.sleep(s['P'])
    elif 'M' in s:
        if s['M']==3:
            PEN_DOWN=True
        if s['M']==5:
            PEN_DOWN=False
           
print('MAX',MAX_X,MAX_Y)
IMG=IMG.crop((0,0,MAX_X+10,MAX_Y+10))
IMG=ImageOps.flip(IMG)
if MAX_X>MAX_Y: IMG=IMG.resize((1600,int(1600/MAX_X*MAX_Y)))
else: IMG=IMG.resize((int(1000/MAX_Y*MAX_X),1000))
IMG.show()
