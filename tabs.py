import curses as c

from constants import *
import buildings as bs
import discounts

headers=["Bonfire","Workshop","Trade","Religion","Space","Time"]
modes=[M_BONFIRE,M_WORKSHOP,M_TRADE,M_RELIGION,M_SPACE,M_TIME]
active=M_BONFIRE



def get_tab(b_selected):
    if b_selected==None:
        return M_BONFIRE
    cat=b_selected["Category"]
    if cat=="Buildings":
        return M_BONFIRE
    if cat=="Trade":
        return M_TRADE
    if cat=="Space":
        return M_SPACE
    if cat=="Chronoforge" or cat=="Void":
        return M_TIME
    return M_RELIGION

def get_tab_name(tab):
    for i in range(len(modes)):
        if modes[i]==tab:
            return headers[i]
    if tab==M_TABLE:
        return "Table"
    if tab==M_HELP:
        return "Help"
    if tab==M_ABOUT:
        return "About"

def show_header(s):
    s.clear()
    for i in range(len(headers)):
        x=i*TAB_LEN
        if modes[i]==active:
            caption=f"{headers[i]}({modes[i]})"
            caption+=" "*(TAB_LEN-len(caption)-1)
            s.addstr(0,x,caption,c.color_pair(SEL_TAB))
            s.addstr("|",c.color_pair(INACTIVE_TAB))
        else:
            caption=f"{headers[i]}({modes[i]})"
            caption+=" "*(TAB_LEN-len(caption)-1)+"|"
            s.addstr(0,x,caption,c.color_pair(INACTIVE_TAB))
    s.chgat(c.color_pair(INACTIVE_TAB))
    s.addstr(0,77,"[",c.color_pair(INACTIVE_TAB)|c.A_BOLD)
    s.addstr(0,78,"X",c.color_pair(ATTENTION_INACTIVE))
    s.addstr(0,79,"]",c.color_pair(INACTIVE_TAB)|c.A_BOLD)

def show_footer(s):
    hint=""
    if active==M_HELP:
        hint="Esc:Close|F1:About|Up/Down:Scroll"
    if active==M_ABOUT:
        hint=f"F10:Exit|Up/Down:Scroll|F4:Continue|F7:Hide/Show on startup (now: {'show' if discounts.show_disclaimer==1 else 'hide'})"
    if active==M_EDIT:
        hint="Esc:Abort|Enter:Confirm|Scientific, integer and KG formats allowed"
    if active==M_TABLE:
        hint="F1:Help|F10:Exit|Esc:To "+get_tab_name(get_tab(bs.b_selected))+"|Up/Down:Scroll|[ and ]:Select|Tab:Format"
    if active==M_WORKSHOP:
        hint="F1:Help|F10:Exit|Esc:To Bonfire|1..8:Select tab|Letters:Select option"
    if active==M_BONFIRE:
        hint="F1:Help|F10:Exit|1..8:Select tab|Ctrl or Alt+Letter:Select building|Tab:Theme"
    if active in [M_RELIGION,M_SPACE,M_TIME,M_TRADE]:
        hint="F1:Help|F10:Exit|1..8:Select tab|Letters:Select building|Tab:Theme"
    if active==M_HIDDEN_TEST:
        hint="No Help|F10:Exit|Space:Next page|Esc:Abort"
    if active==M_DATABASE:
        hint="No Help|F10:Exit|A:Select folder|B:Parse sources|Esc:Cancel"
    s.move(24,0)
    key=True
    for ch in hint:
        if ch==":":
            key=False
        if ch=="|":
            key=True
            s.addstr(ch,c.color_pair(INACTIVE_TAB)|c.A_BOLD)
        else:
            if key:
                s.addstr(ch,c.color_pair(KEY))
            else:
                s.addstr(ch,c.color_pair(INACTIVE_TAB))
    s.clrtoeol()
    s.chgat(c.color_pair(INACTIVE_TAB))
    s.refresh()


def gen_attr(y,x):
    if y==0:
        return c.color_pair(OTHER_BTN)
    if y%2==0:
        return c.color_pair(EVEN_BTN)
    else:
        return c.color_pair(ODD_BTN)

def gen_coord(col,row):
    x=3+col*(BUTTON_LEN+1)
    y=row+3
    return (y,x)

if __name__=="__main__":
    print("Not main module! ("+__file__+")")