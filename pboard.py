from nokolaser import *

polttovali=2

POWER=500

XOYO=2

def tum(x): return 2.54*(x+XOYO)

def dilpin(xl,yl):
    xl=tum(xl)
    yl=tum(yl)
    for y in range(0,12,polttovali):
        yy=yl+(y-6)/10
        Move(xl-2,yy)
        Laser(xl+2,yy,power=POWER)


def DIL(xl,yl,size=(3,8)):
    for y in range(size[1]):
        dilpin(xl,yl+y)
        dilpin(xl+size[0]-1,yl+y)

def tmove(x,y):  Move(tum(x),tum(y))

def tlaser(x,y):  Laser(tum(x),tum(y),power=POWER)

XPREV=0
YPREV=0
def pmove(x,y):
    global  XPREV,YPREV
    XPREV=x
    YPREV=y

def plaser(x,y,p=2):
    global  XPREV,YPREV, POWER
    POWER=200
    if abs(XPREV-x) > abs(YPREV-y):
        for z in range(-p,p+1,polttovali):
            Move(tum(XPREV),tum(YPREV)+(z/10))
            Laser(tum(x),tum(y)+(z/10),power=POWER)
    else:
        for z in range(-p,p+1,polttovali):
            Move(tum(XPREV)+(z/10),tum(YPREV))
            Laser(tum(x)+(z/10),tum(y),power=POWER)
    XPREV=x
    YPREV=y

dilsize=(6,10)
vali=10
kpl=1
DIL(kpl*vali,0,dilsize)
for x in range(0,kpl*vali,vali):
    DIL(x,0,dilsize)
    for y in range(dilsize[1]):
        pmove(x+0.8,y)
        plaser(x+1.5,y+0.5)
        plaser(x+vali-1.5,y+0.5)
        plaser(x+vali-0.8,y)
        pmove(x+dilsize[0]-1,y)
        plaser(x+vali-1.5,y)
        plaser(x+vali-0.8,y-0.5)
        plaser(x+vali+0.8,y-0.5)
        plaser(x+vali+1.5,y)
        plaser(x+vali+dilsize[0]-1,y)

def grid():
    for x in range(0,100,10):
        Move(x,0)
        Laser(x,100)
    for x in range(0,100,10):
        Move(0,x)
        Laser(100,x)        
