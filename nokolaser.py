#! /usr/bin/python3

# nokolaser = output to "gcode.gcode"
# nokolaser send = send "gcode.gcode" to laser
# nokolaser con = output directly to laser

from PIL import Image, ImageFont, ImageDraw  
import serial,time,sys,math,os,datetime,glob,atexit
ser = serial.Serial()

PRINTING=False
GFILE=""
laskuri=0
try:
    if sys.argv[1]=='con':laskuri=5
except: pass
try:
    if sys.argv[1]=='send':laskuri=5
except: pass
while laskuri>0:
    ser.port = "/dev/ttyACM0"
    try: ser.open() ; break
    except:
        ser.port = "/dev/ttyACM1"
        try: ser.open() ; break
        except:
            print('EI PORTTIA')
            laskuri-=1
            time.sleep(0.2)
if laskuri>1:
    ser.baudrate = 9600
    ser.timeout = 0.5
    ser.xonoff = True
    PRINTING=False
else:
    PRINTING=True
    try:
        name=sys.argv[1]
    except:
        name='gcode.gcode'
    GFILE=open(name,'w')
    print("")
    print("No Laser, printing to file",name)
    print("")
    GFILE.write(";from nokolaser\n")
    
def save_status():
    f=open('STASI.py','w')
    f.write('X_NOW='+str(X_NOW)+';Y_NOW='+str(Y_NOW))
    f.close()
            
X_NOW=0
Y_NOW=0
if not os.path.exists('STASI.py'): save_status()
from STASI import *
file_mod_time=datetime.datetime.fromtimestamp(os.path.getmtime('STASI.py'))
today=datetime.datetime.today()
age=today-file_mod_time
print('Welcome back after',age.seconds,'seconds')
if  age.seconds > 1800 and (X_NOW != 0 or Y_NOW != 00):
    print('*** TOO OLD STATUS :',X_NOW,Y_NOW) 
    print('    Move Manually:')
    X_NOW=0
    Y_NOW=0
    save_status()
print('*** STATUS:',X_NOW,',',Y_NOW)
print(glob.glob('*.png'))
print(glob.glob('*.jpg'))

def sendaus(x):
    if not PRINTING:
        ser.timeout = 0.01
        iik=str(ser.read(40))
        if 'ok' in iik:
            time.sleep(1)
            print('Ylijäämä=',iik)
        if len(x)>1: print('sendaus:',x.decode("utf-8")[:-1])
        ser.write(x)
        ser.timeout = 1
        s=str(ser.read(5))
        if "err" in s:
            print('ERROR')
            input('Press Enter to continue')
        elif "ok" in s: pass
        elif len(s) < 5:
            print('WAIT',end="")
            while len(s) < 5:
                time.sleep(0.5)
                s=str(ser.read(5))
                print('.',end="")
            print()
        else:
            print('??? ',s)
    else:
        print('gcode:',x.decode("utf-8"))
        GFILE.write(x.decode("utf-8").replace("\r","\n"))

   
def loppu():
    seis()
    if PRINTING:
        GFILE.write("; Loppu\n")
        GFILE.close()
    print('Hyvasti')
atexit.register(loppu)

       
sendaus(b'G00\r')
sendaus(b'G17\r')
sendaus(b'G40\r')
sendaus(b'G21\r')
sendaus(b'G54\r')
sendaus(b'G90\r')
sendaus(b'M8\r')
sendaus(b'M5\r')

LASER_ON=False
Previous_X=0    
Previous_Y=0    

def seis():
    global LASER_ON
    if LASER_ON or not PRINTING:
        LASER_ON=False
        sendaus(b'M5\r')

GLOBAL_X=0
GLOBAL_Y=0
def Move_raw(x,y):
    global LASER_ON,Previous_X,Previous_Y
    Previous_X=x
    Previous_Y=y
#    sendaus(bytes("G0 X{} Y{}\r".format(x+GLOBAL_X,y+GLOBAL_Y),encoding='UTF-8'))
    sendaus(bytes("G0 X{:.3f} Y{:.3f}\r".format(x+GLOBAL_X,y+GLOBAL_Y),encoding='UTF-8'))

def Move(x,y):
    global LASER_ON,Previous_X,Previous_Y
    Previous_X=x
    Previous_Y=y
    if LASER_ON:
        seis()
        Move_raw(x,y)

POWER=975
SPEED=2400
def Laser(x,y):
    global LASER_ON,Previous_X,Previous_Y
    power=POWER
    speed=SPEED
    if not LASER_ON:
        Move_raw(Previous_X,Previous_Y)
        sendaus(bytes("G1S{}F{}\r".format(power,speed),encoding='UTF-8'))
        sendaus(b'M8\r')
        sendaus(b'M3\r')
        LASER_ON=True
    Previous_X=x
    Previous_Y=y
    sendaus(bytes("G1 X{:.3f} Y{:.3f}\r".format(x+GLOBAL_X,y+GLOBAL_Y),encoding='UTF-8'))


def sleep(seconds):
    sendaus(b'M5\r')
    sendaus(bytes("G4 P{}\r".format(seconds),encoding='UTF-8')) #Plotterissa G4-virhe
    if not PRINTING: time.sleep(seconds)
    
def Frame(x,y):
    Move(0,0)
    Laser(x,0)
    Laser(x,y)
    Laser(0,y)
    Laser(0,0)

Polttoa=False    
def plot2(img,x,y,h,vali,musta):
    global Polttoa
    p=img.getpixel((x,h-y-1))
    v=(p[0]+p[1]+p[2])/3
    if v<musta:
        if not Polttoa:
            Move(x*vali,y*vali)
            Polttoa=True
    else:
        plot3(x,y,vali)
        
def plot3(x,y,vali):
    global Polttoa
    if Polttoa:
        Laser(x*vali,y*vali)
        Polttoa=False

def plot_image(i,mm=0,h=0,vali=0.5,musta=130,kehys=False,
               hori=False,sure=False):
    global POWER,SPEED
    Move_raw(0,0)
    w=int(mm/vali)
    if type(i) == type('string'): img=Image.open(i)
    else: img=i
    if w>0:
        if h>0: img=img.resize((w,h))
        else:
            s=img.size
            h=int(s[1]/(s[0]/w))
            img=img.resize((w,h))
    else:
        s=img.size
        w=s[0]
        h=s[1]
    if not sure:
        print('New Size:',w,',',h," cm:",w*vali/10,',',h*vali/10)
        img.show()
        input('Enter to continue')
    if kehys:
        jemma=POWER,SPEED
        POWER,SPEED=10,6000
        Frame(w*vali,h*vali)
        POWER,SPEED=jemma
        sleep(10)
    if hori:
        for y in range(h):
            for x in range(w): plot2(img,x,y,h,vali,musta)
            plot3(x,y,vali)
            seis()
    else:
        for x in range(w):
            for y in range(h): plot2(img,x,y,h,vali,musta)
            plot3(x,y,vali)
            seis()

def plot_photo(i,mm,grad=8,vali=0.8,kehys=False):
    global POWER,GLOBAL_X,GLOBAL_Y
    if vali=="laser": vali=0.8
    if vali=="plotter": vali=2
    for darkness in range(grad):
        POWER=int(200+600/grad*(darkness+1))
        musta=int(255-255/(grad+1)*(darkness+1))
        if darkness%2==0:
            hori=True
            GLOBAL_Y+=2*vali/grad
        else:
            hori=False
            GLOBAL_X+=2*vali/grad
        plot_image(i,mm,sure=True,musta=musta,hori=hori,vali=vali,kehys=kehys)
        kehys=False

def plot_circle(xo=50,yo=50,r=30,start=0,end=360):
    step=10
    for a in range(start,end+step,step):
         x=r*math.cos(math.radians(a))
         y=r*math.sin(math.radians(a))
         if a==start:
             Move(xo+x,yo+y)
         else:
             Laser(xo+x,yo+y)

def paperin_poltto():
    global POWER,SPEED
    POWER=500
    SPEED=1000

def paperin_leikkuu():
    global POWER,SPEED
    POWER=975
    SPEED=2400
    
def banneri(text,w,h=50,vali=0.5):
    l=len(text)
    huu=h
    image = Image.new(mode="RGB",size=(int(l*huu/1.5),int(huu*1.1)),color="white")  
    draw = ImageDraw.Draw(image)  
    font = ImageFont.truetype('/usr/share/fonts/CreteRound-Regular.ttf',h)  
    draw.text((10,-int(huu/5)), text, font = font, fill='black', align ="left")  
    plot_image(image,w,hori=True,vali=vali)
    Move_raw(0,0)

def curved_box(x,y,r):
    plot_circle(r,r,r,180,270)
    Move(0+r,0)
    Laser(x-r,0)
    plot_circle(x-r,r,r,270,360)
    Move(x,r)
    Laser(x,y-r)
    plot_circle(x-r,y-r,r,0,90)
    Move(x-r,y)
    Laser(r,y)
    plot_circle(r,y-r,r,90,180)
    Move(0,y-r)
    Laser(0,r)
    
def filesendaus(x):
    if not PRINTING:
        f=open(x,"r")
        while True:
            y=f.readline()
            if not y : break
            sendaus(bytes(y,encoding='UTF-8'))
            time.sleep(0.01)
        f.close()
if not PRINTING:
    if sys.argv[1]=='send':
        try:f=sys.argv[2]
        except: f='gcode.gcode'
        print('SENDING:',f)
        time.sleep(10)
        filesendaus(f)
        loppu()
        os._exit(1)
 
        
