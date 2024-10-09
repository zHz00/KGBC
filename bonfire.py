import curses as c

from constants import *
import tabs
import discounts
import table
import buildings as bs


def show(s):
    cur_b=0
    letter_counter_l=0
    letter_counter_r=0
    (y,x)=tabs.gen_coord(0,0)
    s.addstr(y-1,x,"CTRL+",c.color_pair(ATTENTION)|c.A_BOLD)
    (y,x)=tabs.gen_coord(2,0)
    s.addstr(y-1,x,"ALT+",c.color_pair(ATTENTION)|c.A_BOLD)
    for b in bs.buildings:
            if b["Category"]!="Buildings":
                continue
            if cur_b%2==0:
                letter_counter_cur=letter_counter_l
                letter_counter_l+=1
            else:
                letter_counter_cur=letter_counter_r
                letter_counter_r+=1
            b["Letter"]=chr(65+letter_counter_cur)
            b["Side"]= (cur_b%2==0)
            if b["Upgradable"]==0:
                (y,x)=tabs.gen_coord((cur_b%2)*2,cur_b//2)
                cur_b+=1
            if b["Upgradable"]==1:
                (y,x)=tabs.gen_coord((cur_b%2)*2,cur_b//2)
                # skip cur_b+=1
            if b["Upgradable"]==2:
                (y,x)=tabs.gen_coord((cur_b%2)*2+1,cur_b//2)
                cur_b+=1
            b["x"]=x
            b["y"]=y
            letter=chr(65+letter_counter_cur)
            prefix="["+discounts.huts_list[discounts.huts_idx]+"]" if (b["Name"]=="Hut" and discounts.huts_idx!=0) else ""
            postfix=""
            if discounts.policies_active[1]==1 and b["Name"]=="Log House":#fascism
                postfix="[Fas]"
            if discounts.policies_active[2]==1 and b["Name"]=="Factory":#communism
                postfix="[Comm]"
            if discounts.policies_active[0]==1 and b["Name"]in ["Mint","Tradepost","Temple"]:#liberalism
                postfix="[Lib]"
            full_title=prefix+b["Name"]+postfix
            filler=(BUTTON_LEN-len(full_title)-2)*" "
            s.addstr(y,x,letter+":"+full_title+filler,tabs.gen_attr(y,x))

    (y,x)=tabs.gen_coord(2,0)
    s.addstr(23,x,f"Global discount: {round(discounts.global_values[discounts.global_idx],3)}%")
    s.refresh()

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
    if x_mouse!=0 and y_mouse!=0 and m[4]&c.BUTTON1_PRESSED:
        for b in bs.buildings:
            if b["Category"]=="Buildings":
                if x_mouse>=b["x"] and x_mouse<b["x"]+BUTTON_LEN and y_mouse==b["y"]:
                    bs.b_selected=b
                    table.reset_table()
                    return M_TABLE
        return M_BONFIRE
    result="[NONE]"
    for b in bs.buildings:
        if b["Category"]=="Buildings":
            if b["Letter"]==letter:
                if ctrl and b["Side"]==True:
                    result=b["Name"]
                    bs.b_selected=b
                    break
                if alt and b["Side"]==False:
                    result=b["Name"]
                    bs.b_selected=b
                    break
    s.addstr(24,0,result,c.color_pair(OTHER_BTN))
    if result!="[NONE]":
        table.reset_table()
        return M_TABLE
    else:
        return M_BONFIRE

if __name__=="__main__":
    print("Not main module! ("+__file__+")")