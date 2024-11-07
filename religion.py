import curses as c

from constants import *
import buildings as bs
import tabs
import discounts
import table

def show(s):
    cur_b=0
    cur_str=0
    s.addstr(3,COL_R_0,"Ziggurats:")
    for b in bs.buildings:
        if b["Category"]!="Ziggurats":
            continue
        letter=chr(65+cur_b)
        b["Letter"]=letter
        filler=(BUTTON_LEN_L-len(b["Name"])-2)*" "
        y=5+cur_str
        x=COL_R_0
        b["y"]=y
        b["x"]=x
        s.addstr(y,x,letter+":"+b["Name"]+filler,tabs.gen_attr(y,x))
        cur_b+=1
        cur_str+=1

    if discounts.policies_active[0]==1:
        discount_info_gold="Gold: -20%"
    else:
        discount_info_gold="Gold: -0%"

    s.addstr(cur_str+6,COL_R_0,discount_info_gold)


    cur_str=0
    s.addstr(3,COL_R_1,"Order of the Sun:")
    for b in bs.buildings:
        if b["Category"]!="Order of the Sun":
            continue
        if b["Ratio"]==0:
            b["Letter"]=""
            b["y"]=b["x"]=0
            continue
        letter=chr(65+cur_b)
        b["Letter"]=letter
        filler=(BUTTON_LEN_L-len(b["Name"])-2)*" "
        y=5+cur_str
        x=COL_R_1
        b["y"]=y
        b["x"]=x
        s.addstr(y,x,letter+":"+b["Name"]+filler,tabs.gen_attr(y,x))
        cur_b+=1
        cur_str+=1

    ph_mul=discounts.get_philosopher_mul()
    discount_info=f"Discount: -{round((1-ph_mul)*100.0,2)}%"
    if discounts.policies_active[0]==1:
        discount_info_gold_order=f"Gold: -{round((1-ph_mul*0.8)*100.0,2)}%"
    else:
        discount_info_gold_order="Gold: -0%"

    s.addstr(cur_str+6,COL_R_1,discount_info)
    s.addstr(cur_str+7,COL_R_1,discount_info_gold_order)

    cur_str=0
    s.addstr(3,COL_R_2,"Cryptotheology:")
    for b in bs.buildings:
        if b["Category"]!="Cryptotheology":
            continue
        letter=chr(65+cur_b)
        b["Letter"]=letter
        filler=(BUTTON_LEN_L-len(b["Name"])-2)*" "
        y=5+cur_str
        x=COL_R_2
        b["y"]=y
        b["x"]=x
        s.addstr(y,x,letter+":"+b["Name"]+filler,tabs.gen_attr(y,x))
        cur_b+=1
        cur_str+=1

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
            if b["Category"] in ["Ziggurats","Order of the Sun","Cryptotheology"]:
                if x_mouse>=b["x"] and x_mouse<b["x"]+BUTTON_LEN_L and y_mouse==b["y"]:
                    bs.b_selected=b
                    table.reset_table()
                    return M_TABLE
    for b in bs.buildings:
        if b["Category"] in ["Ziggurats","Order of the Sun","Cryptotheology"]:
            if b["Letter"]==letter:
                if letter=="[" and ctrl==True:
                    return M_RELIGION
                result=b["Name"]
                bs.b_selected=b
                break
    #s.addstr(24,0,result,c.color_pair(OTHER_BTN))
    if result!="[NONE]":
        table.reset_table()
        return M_TABLE
    else:
        return M_RELIGION

if __name__=="__main__":
    print("Not main module! ("+__file__+")")