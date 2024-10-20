import curses as c

from constants import *
import tabs
import discounts
import table
import buildings as bs


def show(s):
    cur_b=0
    planet=""
    space_oil=0
    for b in bs.buildings:
            if b["Category"]!="Space":
                continue
            if b["Name"]=="Space Shuttle" or b["Name"]=="Navigation Relay":
                b["x"]=b["y"]=0
                b["Letter"]=""
                continue #not implemented yet
            letter=chr(65+cur_b)
            b["Letter"]=letter
            filler=(BUTTON_LEN_L-len(b["Name"])-2)*" "
            y=2+cur_b
            x=35
            b["y"]=y
            b["x"]=x
            if(b["Planet"]!=planet):
                planet=b["Planet"]
                s.addstr(y,15,b["Planet"]+":")
            s.addstr(y,x,letter+":"+b["Name"]+filler,tabs.gen_attr(y,x))
            if b["Name"] in discounts.space_oil_list:
                s.addstr(" |",c.A_BOLD)
                space_oil+=1
                if space_oil==2:
                    s.addstr(f"Elevators: {discounts.elevators}")
                if space_oil==3:
                    s.addstr(f"Oil: -{round((1-discounts.get_space_oil_mul())*100,1)}%")
            cur_b+=1

def react(s,ch,m,alt_ch):
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
            if b["Category"]=="Space":
                if x_mouse>=b["x"] and x_mouse<b["x"]+BUTTON_LEN_L and y_mouse==b["y"]:
                    bs.b_selected=b
                    table.reset_table()
                    return M_TABLE
    for b in bs.buildings:
        if b["Category"]=="Space":
            if b["Letter"]==letter:
                result=b["Name"]
                bs.b_selected=b
                break
    s.addstr(24,0,result,c.color_pair(OTHER_BTN))
    if result!="[NONE]":
        table.reset_table()
        return M_TABLE
    else:
        return M_SPACE

if __name__=="__main__":
    print("Not main module! ("+__file__+")")