from constants import *
import curses as c

import buildings as bs

MAX_LINES_MENU=18
res_idx = 0
res_skip = 0
ret_mode=0
x0=0
x1=0
y0=0
y1=0

def show(s):
    global res_idx,res_skip
    global x0,x1,y0,y1
    op_list=["None"]
    op_list.extend(bs.res_list)
    idx=res_idx
    skip=res_skip
    cap="Resource List"
    w1=20
    w2=0
    w3=0
    cap1=cap
    lines=len(op_list)
    if lines>MAX_LINES_MENU:
        lines=MAX_LINES_MENU

    if idx>=MAX_LINES_MENU:
        skip+=idx-MAX_LINES_MENU+1
        idx=MAX_LINES_MENU-1
    res_idx=idx
    res_skip=skip
    w1=len(cap)
    for op in op_list:
        if len(op)>w1:
            w1=len(op)
    w_fast=5
    w1+=w_fast#for fast-select numbers
    h=GLOBAL_H-2-1#one for header
    offset_y=0
    if lines>=h:
        offset_y=0
    else:
        offset_y=int((h-lines)/2)
    offset_x=int((GLOBAL_W-w1-w2-w3-4)/2)#4 for |
    header=f"|{cap1:{w1}}|"
    x0=offset_x
    x1=x0+len(header)-1
    y0=offset_y+1
    y1=y0+lines-1
    s.addstr(offset_y,offset_x,header,c.color_pair(INACTIVE_TAB)|c.A_BOLD)

    for y in range(lines):
        op=op_list[y+skip]
        fast_sel="?"
        if y<=8:
            fast_sel=chr(48+1+y)
        else:
            fast_sel=chr(65+y-9)
        finalizer="|"
        if y==lines-1:#last line
            if len(op_list)>MAX_LINES_MENU:#scrolling
                if y+skip<len(op_list)-1:#there are more lines
                    finalizer="V"
                else:
                    finalizer="|"
        if y==0:#first line
            if len(op_list)>MAX_LINES_MENU:#scrolling
                if y+skip>0:#there are more lines
                    finalizer="^"
                else:
                    finalizer="|"

        info=f"[{fast_sel}]{op}"
        info="|"+f"{info:{w1}}"+finalizer
        if y==idx:
            s.addstr(y+offset_y+1,offset_x,info,c.color_pair(SEL_TAB))
        else:
            s.addstr(y+offset_y+1,offset_x,info,c.color_pair(INACTIVE_TAB))
    s.refresh()

def react(search_win,ch,m,alt_ch):
    global res_idx,res_skip,res_final
    op_list=["None"]
    op_list.extend(bs.res_list)
    if len(op_list)>MAX_LINES_MENU:
        list_len=MAX_LINES_MENU
    else:
        list_len=len(op_list)
    idx=res_idx
    skip=res_skip
    global mode

    key=""
    key=c.keyname(ch).decode("utf-8")
    key=key.upper()
    letter=' '
    ctrl=False
    alt=False
    x_mouse=0
    y_mouse=0
    if m!=None:
        x_mouse=m[1]
        y_mouse=m[2]
    if m!=None:
        if m[4]&c.BUTTON4_PRESSED:
            if idx>0:
                idx-=1
            else:
                if skip>0:
                    skip-=1
                else:
                    if len(op_list)>MAX_LINES_MENU:
                        idx=MAX_LINES_MENU-1
                        skip=len(op_list)-MAX_LINES_MENU
                    else:
                        idx=len(op_list)-1
        if m[4]&0x200000:
            idx+=1
            if idx>=list_len:
                idx-=1
                skip+=1
                if skip+idx>=len(op_list):
                    skip=0
                    idx=0
        if m[4]&c.BUTTON3_PRESSED:
            return ret_mode
    if x_mouse!=0 or y_mouse!=0:
        if x_mouse>=x0 and x_mouse<=x1 and y_mouse>=y0 and y_mouse<=y1:
            selected=y_mouse-y0
            if m[4]&c.BUTTON1_DOUBLE_CLICKED or m[4]&c.BUTTON2_PRESSED or m[4]&0x10000000:
                idx=selected
                key="^M"
            if m[4]&c.BUTTON1_PRESSED:
                idx=selected

    if len(key)==1:
        letter=key
    else:
        if key.startswith("^"):
            ctrl=True
            letter=key[1]
        if key.startswith("ALT_") or key.startswith("M-"):
            alt=True
            letter=key[-1]
    if ch==27 and len(alt_ch)==0:
        return ret_mode
    if ch in range(49,49+9):#1...9
        ch=ch-49
        if ch<len(op_list):
            idx=ch
            key="^M"#then skip to section below
    if ch in range(65,65+26):#A-Z
        ch=ch-65+9
        if ch<len(op_list):
            idx=ch
            key="^M"#then skip to section below
    if ch in range(97,97+26):#A-Z
        ch=ch-97+9
        if ch<len(op_list):
            idx=ch
            key="^M"#then skip to section below
    if key=="KEY_UP" :
        if idx>0:
            idx-=1
        else:
            if skip>0:
                skip-=1
            else:
                if len(op_list)>MAX_LINES_MENU:
                    idx=MAX_LINES_MENU-1
                    skip=len(op_list)-MAX_LINES_MENU
                else:
                    idx=len(op_list)-1
    if key=="KEY_DOWN" :
        if idx+1<list_len:
            idx+=1
        else:
            if idx+1>=list_len:
                skip+=1
                if idx+skip>=len(op_list):
                    idx=0
                    skip=0
    if key=="KEY_HOME" or alt_ch=="[H" or alt_ch=="[1~":
        idx=0
        skip=0
    if key=="KEY_END" or key=="KEY_A1" or alt_ch=="[4~":
        idx=len(op_list)-1
        if idx>=MAX_LINES_MENU:
            idx=MAX_LINES_MENU-1
            skip=len(op_list)-MAX_LINES_MENU
    if key=="^M" or key=="^J":
        res_idx=idx
        res_skip=skip
        bs.res_highlight=res_idx+res_skip-1#-1 is for "None"
        return ret_mode
    res_idx=idx
    res_skip=skip
    return M_RESOURCE_SEL

if __name__=="__main__":
    print("Not main module! ("+__file__+")")