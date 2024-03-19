#! /usr/bin(/Python3

from PIL import Image, ImageFont, ImageDraw  
import serial,time,sys,math,os,datetime,glob
ser = serial.Serial()

while True:
    ser.port = "/dev/ttyACM0"
    try: ser.open() ; break
    except:
        ser.port = "/dev/ttyACM1"
        try: ser.open() ; break
        except:
            print('EI PORTTIA')
            time.sleep(1)

ser.baudrate = 9600
ser.timeout = 0.5
ser.xonoff = True

def save_status():
    f=open('STATUS.py','w')
    f.write('X_NOW='+str(X_NOW)+';Y_NOW='+str(Y_NOW))
    f.close()
            
X_NOW=0
Y_NOW=0
if not os.path.exists('STATUS.py'): save_status()
from STATUS import *
file_mod_time=datetime.datetime.fromtimestamp(os.path.getmtime('STATUS.py'))
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
    ser.timeout = 0.01
    ser.read(40)
    print('sendaus:',x,end=":")
    ser.write(x)
    ser.timeout = 1
    s=str(ser.read(5))
    if "err" in s:
        print('ERROR')
        input('Press Enter to continue')
    elif "ok" in s: print('OK')
    else: print('??? ',s)
"""
def sendaus(x):
    print('sendaus:',x)
    time.sleep(0.5)
"""    
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
    LASER_ON=False
    sendaus(b'M5\r')

def Move_raw(x,y):
    global LASER_ON,Previous_X,Previous_Y
    Previous_X=x
    Previous_Y=y
    sendaus(bytes("G0 X{} Y{}\r".format(x,y),encoding='UTF-8'))
    
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
    if not LASER_ON:
        Move_raw(Previous_X,Previous_Y)
        sendaus(bytes("G1S{}F{}\r".format(POWER,SPEED),encoding='UTF-8'))
        sendaus(b'M8\r')
        sendaus(b'M3\r')
        LASER_ON=True
    Previous_X=x
    Previous_Y=y
    sendaus(bytes("G1 X{} Y{}\r".format(x,y),encoding='UTF-8'))

def Frame(x,y):
    Move(0,0)
    Laser(x,0)
    Laser(x,y)
    Laser(0,y)
    Laser(0,0)
    seis()

Polttoa=False    
def plot2(img,x,y,h,vali,musta):
    global Polttoa
    p=img.getpixel((x,h-y-1))
    v=(p[0]+p[1]+p[2])/3
    if p[0]<musta:
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

def plot_image(i,mm=0,h=0,vali=0.5,musta=130,kehys=False,hori=False):
    Move_raw(0,0)
    w=int(mm/vali)
    if type(i) == type('string'): img=Image.open(i)
    else: img=i
    if w>0:
        if h>0:
            img=img.resize((w,h))
        else:
            s=img.size
            h=int(s[1]/(s[0]/w))
            img=img.resize((w,h))
    else:
        s=img.size
        w=s[0]
        h=s[1]
    print('New Size:',w,',',h," cm:",w*vali/10,',',h*vali/10)
    img.show()
    input('Enter to continue')
    if kehys: Frame(w*vali,h*vali)
    if hori:
        for y in range(h):
            for x in range(w): plot2(img,x,y,h,vali,musta)
            plot3(x,y,vali)
            seis()
    else:
        for x in range(w):
            seis()
            for y in range(h): plot2(img,x,y,h,vali,musta)
            plot3(x,y,vali)
            seis()
    seis()


def plot_circle(r=30,xo=50,yo=50):
     step=10
     for a in range(0,360+step,step):
         x=r*math.cos(math.radians(a))
         y=r*math.sin(math.radians(a))
         if a==0:
             Move(xo+x,yo+y)
         else:
             Laser(xo+x,yo+y)
     seis()        

def paperi():
    global POWER,SPEED
    POWER=500
    SPEED=1000

def banneri(text,w,h=50,vali=0.5):
    l=len(text)
    huu=h
    image = Image.new(mode="RGB",size=(int(l*huu/1.5),int(huu*1.1)),color="white")  
    draw = ImageDraw.Draw(image)  
    font = ImageFont.truetype('/usr/share/fonts/CreteRound-Regular.ttf',h)  
    draw.text((10,-int(huu/5)), text, font = font, fill='black', align ="left")  
    plot_image(image,w,hori=True,vali=vali)
    Move_raw(0,0)
    

    
