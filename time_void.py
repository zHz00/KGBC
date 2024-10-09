import curses as c

from constants import *
import tabs
import discounts
import table
import buildings as bs

def show(s):
    cur_b=0
    col0=25
    col1=40
    s.addstr(2,col0,"Chronoforge:")
    for b in bs.buildings:
        if b["Category"]!="Chronoforge":
            continue
        letter=chr(65+cur_b)
        b["Letter"]=letter
        filler=(BUTTON_LEN_L-len(b["Name"])-2)*" "
        y=2+cur_b
        x=col1
        b["y"]=y
        b["x"]=x
        s.addstr(y,x,letter+":"+b["Name"]+filler,tabs.gen_attr(y,x))
        cur_b+=1

    s.addstr(4+cur_b,col0,"Void:")
    for b in bs.buildings:
        if b["Category"]!="Void":
            continue
        letter=chr(65+cur_b)
        b["Letter"]=letter
        filler=(BUTTON_LEN_L-len(b["Name"])-2)*" "
        y=4+cur_b
        x=col1
        b["y"]=y
        b["x"]=x
        s.addstr(y,x,letter+":"+b["Name"]+filler,tabs.gen_attr(y,x))
        cur_b+=1

def react(s,ch,m):
    key=""
    key=c.keyname(ch).decode("utf-8")
    key=key.upper()
    letter=' '
    ctrl=False
    alt=False
    if len(key)==1:
        letter=key
    else:
        if key.startswith("^"):
            ctrl=True
            letter=key[1]
        if key.startswith("ALT_") or key.startswith("M-"):
            alt=True
            letter=key[-1]
    x_mouse=0
    y_mouse=0
    if m!=None:
        x_mouse=m[1]
        y_mouse=m[2]
    result="[NONE]"
    if x_mouse!=0 and y_mouse!=0 and m[4]&c.BUTTON1_PRESSED:
        for b in bs.buildings:
            if b["Category"] in ["Chronoforge","Void"]:
                if x_mouse>=b["x"] and x_mouse<b["x"]+BUTTON_LEN_L and y_mouse==b["y"]:
                    bs.b_selected=b
                    table.reset_table()
                    return M_TABLE
    for b in bs.buildings:
        if b["Category"] in ["Chronoforge","Void"]:
            if b["Letter"]==letter:
                result=b["Name"]
                bs.b_selected=b
                break
    s.addstr(24,0,result,c.color_pair(OTHER_BTN))
    if result!="[NONE]":
        table.reset_table()
        return M_TABLE
    else:
        return M_TIME