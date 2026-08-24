import math
import curses as c

from constants import *
import utils
import pure_math

magneto=1
sw=1

C0=1
C1=25
C2=40
C3=55
C4=70

INPUT_STR=5
CHANGE_STR=7
BTN_WIDTH=4

swm_coeff=0.15
griffins_machinists=0
griffins_y=0

def bonus(m,s):
    return 100*m*(0.02*(1+swm_coeff*s))

def pollution(m,s):
    return 5*m+s

def magneto_bonus_optimal(m0,s0):
    return 2/3 * (1 + swm_coeff * (5 * m0 + s0))

def steamworks_bonus_optimal(m0,s0,m):
    return  5 * m0 + s0 - 5*m

def steamworks_pollution_optimal(m0,s0):
    bonus_before=bonus(m0,s0)
    s=(math.sqrt(5*bonus_before*swm_coeff/100/0.02)-1)/swm_coeff
    return s

def magneto_pollution_optimal(m0,s0,s):
    bonus_before=bonus(m0,s0)
    m=bonus_before/(100*0.02*(1+swm_coeff*s))
    return m

def show(s):
    global griffins_y
    s.clear()

    name="=== "+"Steamworks & Magneto Calculator"+" ==="
    space=" "*int((GLOBAL_W-len(name))/2)
    info=space+name+space
    s.addstr(0,0,info,c.color_pair(BUILDING_HEADER))
    s.chgat(c.color_pair(BUILDING_HEADER))
    s.addstr(0,0,"[",c.color_pair(INACTIVE_TAB)|c.A_BOLD)
    s.addstr(0,1,"<-",c.color_pair(ATTENTION_INACTIVE))
    s.addstr(0,3,"]",c.color_pair(INACTIVE_TAB)|c.A_BOLD)


    y=3
    s.addstr(y,C0,"")
    s.addstr(y,C1,"A:Steamworks")
    s.addstr(y,C2,"B:Magneto")
    s.addstr(y,C3,"Bonus")
    s.addstr(y,C4,"Pollution")

    bonus_str=f"+{bonus(magneto,sw):.2f}%"
    pollution_str="+"+str(pollution(magneto,sw))

    y=INPUT_STR
    s.addstr(y,C0,"Current")
    s.addstr(y,C1,f"{sw:<{COL_WIDTH}}",c.color_pair(OTHER_BTN))
    s.addstr(y,C2,f"{magneto:<{COL_WIDTH}}",c.color_pair(OTHER_BTN))
    s.addstr(y,C3,f"{bonus_str}")
    s.addstr(y,C4,f"{pollution_str}")

    y=CHANGE_STR
    s.addstr(y,C1," -1 ",c.color_pair(OTHER_BTN))
    s.addstr(y,C1+BTN_WIDTH+4," +1 ",c.color_pair(OTHER_BTN))

    s.addstr(y,C2," -1 ",c.color_pair(OTHER_BTN))
    s.addstr(y,C2+BTN_WIDTH+4," +1 ",c.color_pair(OTHER_BTN))


    y+=1
    s.addstr(y,0,"-"*GLOBAL_W)

    mo1=math.floor(magneto_bonus_optimal(magneto,sw))
    so1=steamworks_bonus_optimal(magneto,sw,mo1)

    if mo1<0 or so1<0:
        mo1="-"
        so1="-"
        bonus_str="-"
        pollution_str="-"
    else:
        bonus_str=f"+{bonus(mo1,so1):.2f}%"
        pollution_str="+"+str(pollution(mo1,so1))

    y+=1
    s.addstr(y,C0,"Optimal bonus 1")
    s.addstr(y,C1,f"{so1}")
    s.addstr(y,C2,f"{mo1}")
    s.addstr(y,C3,f"{bonus_str}")
    s.addstr(y,C4,f"{pollution_str}")

    mo2=math.floor(magneto_bonus_optimal(magneto,sw))+1
    so2=steamworks_bonus_optimal(magneto,sw,mo2)

    if mo2<0 or so2<0:
        mo2="-"
        so2="-"
        bonus_str="-"
        pollution_str="-"
    else:
        bonus_str=f"+{bonus(mo2,so2):.2f}%"
        pollution_str="+"+str(pollution(mo2,so2))

    y+=1
    s.addstr(y,C0,"Optimal bonus 2")
    s.addstr(y,C1,f"{so2}")
    s.addstr(y,C2,f"{mo2}")
    s.addstr(y,C3,f"{bonus_str}")
    s.addstr(y,C4,f"{pollution_str}")

    y+=1
    s.addstr(y,0,"-"*GLOBAL_W)


    so_poll_a=[]
    mo_poll_a=[]

    so_poll_float=steamworks_pollution_optimal(magneto,sw)
    so_poll=math.floor(so_poll_float)
    so_poll_a=[so_poll,so_poll,so_poll+1,so_poll+1]
    mo_poll1=math.floor(magneto_pollution_optimal(magneto,sw,so_poll))
    mo_poll2=math.floor(magneto_pollution_optimal(magneto,sw,so_poll))+1
    mo_poll3=math.floor(magneto_pollution_optimal(magneto,sw,so_poll+1))
    mo_poll4=math.floor(magneto_pollution_optimal(magneto,sw,so_poll+1))+1
    mo_poll_a=[mo_poll1,mo_poll2,mo_poll3,mo_poll4]

    for p in range(4):
        if so_poll_a[p]<0 or mo_poll_a[p]<0:
            mo_str="-"
            so_str="-"
            bonus_str="-"
            pollution_str="-"
        else:
            mo_str=str(mo_poll_a[p])
            so_str=str(so_poll_a[p])
            bonus_str=f"+{bonus(mo_poll_a[p],so_poll_a[p]):.2f}%"
            pollution_str="+"+str(pollution(mo_poll_a[p],so_poll_a[p]))


        y+=1
        s.addstr(y,C0,f"Optimal pollution {p+1}")
        s.addstr(y,C1,f"{so_str}")
        s.addstr(y,C2,f"{mo_str}")
        s.addstr(y,C3,f"{bonus_str}")
        s.addstr(y,C4,f"{pollution_str}")
    y+=1
    s.addstr(y,0,"-"*GLOBAL_W)
    y+=1
    griffins_y=y
    griffins_str=""
    if griffins_machinists==0:
        griffins_str="[ ] C:Griffins Relations: Machinists (Steamworks Magneto bonus: 15%)"
    else:
        griffins_str="[X] C:Griffins Relations: Machinists (Steamworks Magneto bonus: 15.5%)"
    s.addstr(y,C0,griffins_str)

def toggle_griffins():
    global swm_coeff,griffins_machinists
    if griffins_machinists==0:
        griffins_machinists=1
        swm_coeff=0.155
    else:
        griffins_machinists=0
        swm_coeff=0.15

def react(s,ch,m,alt_ch):
    global magneto, sw
    key=""
    key=c.keyname(ch).decode("utf-8")
    key=key.upper()
    letter=' '
    ctrl=False
    alt=False
    x_mouse=0
    y_mouse=0
    event_mouse=0
    if m!=None:
        x_mouse=m[1]
        y_mouse=m[2]
        event_mouse=m[4]
    selected=0
    scroll_up=0
    scroll_down=0
    pressed=0
    if y_mouse==0 and x_mouse in [0,1,2,3] and event_mouse&c.BUTTON1_PRESSED:
        return M_BONFIRE
    if event_mouse&c.BUTTON3_PRESSED:
        return M_BONFIRE
    if x_mouse>=C1 and x_mouse<=C1+COL_WIDTH-1 and y_mouse==INPUT_STR and event_mouse&c.BUTTON1_PRESSED:
        selected=1
        pressed=1
    if x_mouse>=C2 and x_mouse<=C2+COL_WIDTH-1 and y_mouse==INPUT_STR and event_mouse&c.BUTTON1_PRESSED:
        selected=2
        pressed=1

    if x_mouse>=C1 and x_mouse<=C1+BTN_WIDTH-1 and y_mouse==CHANGE_STR and event_mouse&c.BUTTON1_PRESSED:
        scroll_down=1
        selected=1
    if x_mouse>=C1+BTN_WIDTH+4 and x_mouse<=C1+2*BTN_WIDTH+4-1 and y_mouse==CHANGE_STR and event_mouse&c.BUTTON1_PRESSED:
        scroll_up=1
        selected=1

    if x_mouse>=C2 and x_mouse<=C2+BTN_WIDTH-1 and y_mouse==CHANGE_STR and event_mouse&c.BUTTON1_PRESSED:
        scroll_down=1
        selected=2
    if x_mouse>=C2+BTN_WIDTH+4 and x_mouse<=C2+2*BTN_WIDTH+4-1 and y_mouse==CHANGE_STR and event_mouse&c.BUTTON1_PRESSED:
        scroll_up=1
        selected=2
    if x_mouse in [C0,C0+1,C0+2] and y_mouse==griffins_y and event_mouse&c.BUTTON1_PRESSED:
        toggle_griffins()

    if ch==27:
        return M_BONFIRE
    if key=="A" or (selected==1 and pressed==1):
        text=utils.textpad(s,INPUT_STR,C1,COL_WIDTH)
        if len(text)>0:
            try:
                val=pure_math.parse_num(text.strip())
                if val<0:
                    utils.show_message("Number must be >=0!")
                else:
                    sw=int(val)
            except:
                utils.show_message("Invalid input!")
    if key=="B" or (selected==2 and pressed==1):
        text=utils.textpad(s,INPUT_STR,C2,COL_WIDTH)
        if len(text)>0:
            try:
                val=pure_math.parse_num(text.strip())
                if val<0:
                    utils.show_message("Number must be >=0!")
                else:
                    magneto=int(val)
            except:
                utils.show_message("Invalid input!")
    if key=="C":
        toggle_griffins()
    if scroll_up==1 and selected==1:
        sw+=1
    if scroll_down==1 and selected==1:
        sw-=1
        if sw<0:
            sw=0
    if scroll_up==1 and selected==2:
        magneto+=1
    if scroll_down==1 and selected==2:
        magneto-=1
        if magneto<0:
            magneto=0
    return M_SW_MAGNETO


if __name__=="__main__":
    print("Not main module! ("+__file__+")")