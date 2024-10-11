import sqlite3 as sl
import curses as c
import curses.textpad
import ast

import table
from constants import *
import buildings as bs
import tests

import tabs
import bonfire
import workshop
import trade
import religion
import space
import time_void



s = None
keys=""


def show_page(s,mode):
    if mode==M_BONFIRE:
        bonfire.show(s)
    if mode==M_TABLE:
        table.show(s,bs.b_selected)
    if mode==M_WORKSHOP:
        workshop.show(s)
    if mode==M_SPACE:
        space.show(s)
    if mode==M_TIME:
        time_void.show(s)
    if mode==M_RELIGION:
        religion.show(s)
    if mode==M_TRADE:
        trade.show(s)
    if mode==M_HIDDEN_TEST:
        tests.show_hidden_test(s)

def react_key(s,mode,ch):
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

    m=None
    if ch==c.KEY_MOUSE:
        m=c.getmouse()
        x_mouse=m[1]
        y_mouse=m[2]
        if m[4]&c.BUTTON1_PRESSED:
            if y_mouse==0 and (tabs.active not in [M_TABLE,M_HIDDEN_TEST]):
                tab_idx=(x_mouse+1)//TAB_LEN
                if tab_idx < len(tabs.modes):
                    return tabs.modes[tab_idx]
                else:
                    return M_EXIT

    probably_tab_mode=ord(letter)-48
    if probably_tab_mode in tabs.modes and mode not in [M_TABLE,M_HIDDEN_TEST]:
        return probably_tab_mode
    if probably_tab_mode==9:
        return M_HIDDEN_TEST
    if mode==M_BONFIRE:
        return bonfire.react(s,ch,m)
    if mode==M_SPACE:
        return space.react(s,ch,m)
    if mode==M_TIME:
        return time_void.react(s,ch,m)
    if mode==M_TRADE:
        return trade.react(s,ch,m)
    if mode==M_RELIGION:
        return religion.react(s,ch,m)
    if mode==M_TABLE:
        return table.react(s,ch,m)
    if mode==M_WORKSHOP:
        return workshop.react(s,ch,m)
    if mode==M_HIDDEN_TEST:
        return tests.react(s,ch,m)

    

def main(s):
    db_link=sl.connect("kg_db.db")
    db_link.row_factory = sl.Row
    db_cursor=db_link.cursor()
    db_cursor.execute("SELECT * FROM BUILDINGS")
    fetch=db_cursor.fetchall()
    for b in fetch:
        bs.buildings.append({"Category":b["Category"],"Planet":b["Planet"],"Name":b["Name"],"Upgradable":b["Upgradable"],"Ratio":b["Ratio"],"Recipe":ast.literal_eval(b["Recipe"])})

    max_r=0
    for b in bs.buildings:
        if len(b["Recipe"])>max_r:
            max_r=len(b["Recipe"])
    #max recipe len == 6, for moon base and lunar outpost

    c.raw()
    c.mousemask(-1)
    c.mouseinterval(0)
    c.curs_set(0)
    ec=c.can_change_color()
    for i in range(0, curses.COLORS):
        c.init_pair(i+1, i, c.COLOR_BLUE)
    c.init_pair(ODD_BTN, c.COLOR_WHITE,c.COLOR_CYAN)
    c.init_pair(EVEN_BTN, c.COLOR_BLACK,c.COLOR_WHITE)
    c.init_pair(OTHER_BTN, c.COLOR_BLACK,c.COLOR_WHITE)
    c.init_pair(SEL_TAB, c.COLOR_BLACK,c.COLOR_WHITE)
    c.init_pair(INACTIVE_TAB, c.COLOR_WHITE,c.COLOR_BLACK)
    c.init_pair(BK,c.COLOR_WHITE,c.COLOR_BLUE)
    c.init_pair(BK_CURSOR,c.COLOR_BLUE,c.COLOR_WHITE)
    c.init_pair(ATTENTION,c.COLOR_RED|8,c.COLOR_BLUE)
    c.init_pair(ATTENTION_INACTIVE,c.COLOR_RED|8,c.COLOR_BLACK)
    c.init_pair(SEL_LINE,c.COLOR_YELLOW,c.COLOR_BLUE)
    c.init_pair(BK_CURSOR_SEL,c.COLOR_YELLOW|8,c.COLOR_WHITE)
    c.init_pair(BK_SEL,c.COLOR_YELLOW|8,c.COLOR_BLUE)
    c.init_pair(BUILDING_HEADER,c.COLOR_YELLOW|8,c.COLOR_BLACK)
    c.init_pair(KEY,c.COLOR_YELLOW,c.COLOR_BLACK)
    c.init_pair(TEST_OK,c.COLOR_GREEN|8,c.COLOR_BLUE)
    c.init_pair(TEST_FAIL,c.COLOR_RED|8,c.COLOR_BLUE)
    c.init_pair(BK_ALT,c.COLOR_GREEN,c.COLOR_BLUE)

    s.bkgd(' ',c.color_pair(BK))
    s.clear()

    tabs.active=M_BONFIRE

    while True:
        if tabs.active not in [M_TABLE,M_HIDDEN_TEST]:
            tabs.show_header(s)
        show_page(s,tabs.active)
        tabs.show_footer(s)
        ch=s.getch()
        tabs.active=react_key(s,tabs.active,ch)
        if tabs.active==M_EXIT:
            break
        key=c.keyname(ch).decode("utf-8")
        if key=="KEY_F(10)":
            break
 


c.wrapper(main)