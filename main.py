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
import discounts
import help
import db
import pure_math
import utils

themes=[]
themes.append([c.COLOR_WHITE,c.COLOR_CYAN,c.COLOR_CYAN,c.COLOR_WHITE])
themes.append([c.COLOR_BLACK,c.COLOR_CYAN,c.COLOR_CYAN,c.COLOR_BLACK])
themes.append([c.COLOR_WHITE,c.COLOR_YELLOW,c.COLOR_YELLOW,c.COLOR_WHITE])
themes.append([c.COLOR_BLACK,c.COLOR_YELLOW,c.COLOR_YELLOW,c.COLOR_BLACK])
themes.append([c.COLOR_BLACK,c.COLOR_WHITE,c.COLOR_WHITE,c.COLOR_BLACK])



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
    if mode in [M_HELP,M_ABOUT]:
        help.show(s)
    if mode==M_DATABASE:
        db.show(s)
    s.refresh()

def react_key(s,mode,ch,alt_ch):
    global theme_idx
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

    if letter=='I' and ctrl==True and mode!=M_TABLE:#Tab
        discounts.theme=(discounts.theme+1)%(len(themes))
        c.init_pair(ODD_BTN, themes[discounts.theme][0],themes[discounts.theme][1])
        c.init_pair(EVEN_BTN, themes[discounts.theme][2],themes[discounts.theme][3])
        discounts.update_settings()
        discounts.save_settings()
        return mode

    probably_tab_mode=ord(letter)-48
    if probably_tab_mode in tabs.modes and mode not in [M_TABLE,M_HIDDEN_TEST,M_HELP,M_ABOUT]:
        return probably_tab_mode
    if probably_tab_mode==0:
        return M_DATABASE
    if key=="KEY_F(1)" and mode not in [M_HIDDEN_TEST,M_HELP,M_DATABASE]:
        help.page=mode
        return M_HELP
    if key=="KEY_F(1)" and mode==M_HELP:
        help.page=M_ABOUT
        help.line=-1
        return M_ABOUT
    if mode==M_BONFIRE:
        return bonfire.react(s,ch,m,alt_ch)
    if mode==M_SPACE:
        return space.react(s,ch,m,alt_ch)
    if mode==M_TIME:
        return time_void.react(s,ch,m,alt_ch)
    if mode==M_TRADE:
        return trade.react(s,ch,m,alt_ch)
    if mode==M_RELIGION:
        return religion.react(s,ch,m,alt_ch)
    if mode==M_TABLE:
        return table.react(s,ch,m,alt_ch)
    if mode==M_WORKSHOP:
        return workshop.react(s,ch,m,alt_ch)
    if mode==M_HIDDEN_TEST:
        return tests.react(s,ch,m,alt_ch)
    if mode in [M_HELP,M_ABOUT]:
        return help.react(s,ch,m,alt_ch)
    if mode==M_DATABASE:
        return db.react(s,ch,m,alt_ch)

def restore_size():
    c.update_lines_cols()
    if c.LINES<25 or c.COLS<80:
        c.resize_term(25, 80)
        c.update_lines_cols()
        if c.LINES<25 or c.COLS<80:
            utils.show_message("Cannot resize terminal! 80x25 is a minimum!")
            print("Cannot resize terminal! 80x25 is a minimum!")
            exit(1)

def main(s):
    db_link=sl.connect(KG_DB_FILE)
    db_link.row_factory = sl.Row
    db_cursor=db_link.cursor()
    db_cursor.execute("SELECT * FROM BUILDINGS")
    fetch=db_cursor.fetchall()
    buildings_tmp=[]
    for b in fetch:
        buildings_tmp.append({"Category":b["Category"],"Planet":b["Planet"],"Name":b["Name"],"Upgradable":b["Upgradable"],"Ratio":b["Ratio"],"GroupName":b["GroupName"],"Recipe":ast.literal_eval(b["Recipe"])})
        if b["GroupName"] not in bs.groups:
            bs.groups.append(b["GroupName"])

    db_link.close()

    for g in bs.groups:
        for b in buildings_tmp:
            if b["GroupName"]==g:
                bs.buildings.append(b)
    #reorder list using buildings groups

    max_r=0
    for b in bs.buildings:
        if len(b["Recipe"])>max_r:
            max_r=len(b["Recipe"])
    #max recipe len == 6, for moon base and lunar outpost
    if c.COLORS<16:
        b=0#brighness bit
    else:
        b=8

    try:
        discounts.settings=tests.load_tests(discounts.SETTINGS_FILE)
        discounts.load_settings(discounts.settings[0])
    except FileNotFoundError:
        discounts.settings=tests.load_tests(discounts.SETTINGS_FILE_DEFAULT)
        discounts.load_settings(discounts.settings[0])
        if b==0:#8-color mode
            discounts.theme=1#more pretty theme for this mode
        discounts.update_settings()
        discounts.save_settings()


    c.raw()
    c.mousemask(-1)
    c.mouseinterval(0)
    c.curs_set(0)
    ec=c.can_change_color()
    s.clear()
    #for i in range(0, curses.COLORS):
        #s.addstr(f"Color pair: {i};")
        #c.init_pair(i+1, i, c.COLOR_BLUE)

    c.init_pair(ODD_BTN, themes[discounts.theme][0],themes[discounts.theme][1])
    c.init_pair(EVEN_BTN, themes[discounts.theme][2],themes[discounts.theme][3])
    c.init_pair(OTHER_BTN, c.COLOR_BLACK,c.COLOR_WHITE)
    c.init_pair(SEL_TAB, c.COLOR_BLACK,c.COLOR_WHITE)
    c.init_pair(INACTIVE_TAB, c.COLOR_WHITE,c.COLOR_BLACK)
    c.init_pair(BK,c.COLOR_WHITE,c.COLOR_BLUE)
    c.init_pair(ATTENTION,c.COLOR_RED|b,c.COLOR_BLUE)
    c.init_pair(ATTENTION_INACTIVE,c.COLOR_RED|b,c.COLOR_BLACK)
    c.init_pair(SEL_LINE,c.COLOR_YELLOW,c.COLOR_BLUE)
    if b!=0:
        c.init_pair(BK_CURSOR_SEL,c.COLOR_YELLOW|b,c.COLOR_WHITE)
        c.init_pair(BK_CURSOR,c.COLOR_BLUE,c.COLOR_WHITE)
    else:
        c.init_pair(BK_CURSOR_SEL,c.COLOR_YELLOW|b,c.COLOR_BLACK)
        c.init_pair(BK_CURSOR,c.COLOR_WHITE,c.COLOR_BLACK)
    c.init_pair(BK_SEL,c.COLOR_YELLOW|b,c.COLOR_BLUE)
    c.init_pair(BUILDING_HEADER,c.COLOR_YELLOW|b,c.COLOR_BLACK)
    c.init_pair(KEY,c.COLOR_YELLOW,c.COLOR_BLACK)
    c.init_pair(TEST_OK,c.COLOR_GREEN|b,c.COLOR_BLUE)
    c.init_pair(TEST_FAIL,c.COLOR_RED|b,c.COLOR_BLUE)
    c.init_pair(BK_ALT,c.COLOR_YELLOW,c.COLOR_BLUE)
    c.init_pair(RATIO_INFO,c.COLOR_CYAN|b,c.COLOR_BLUE)

    if b!=0:
        c.init_pair(HELP_NORMAL,c.COLOR_BLACK|b,c.COLOR_BLACK)
    else:
        c.init_pair(HELP_NORMAL,c.COLOR_WHITE,c.COLOR_BLACK)#black on black: not visible
    c.init_pair(HELP_HEADER,c.COLOR_WHITE|b,c.COLOR_BLACK)
    c.init_pair(HELP_BOLD,c.COLOR_MAGENTA|b,c.COLOR_BLACK)
    c.init_pair(HELP_ITALIC,c.COLOR_CYAN|b,c.COLOR_BLACK)
    c.init_pair(HELP_NAME,c.COLOR_YELLOW,c.COLOR_BLACK)

    s.bkgd(' ',c.color_pair(BK))
    s.clear()
    s.refresh()

    if discounts.show_disclaimer==1:
        help.page=M_ABOUT
        tabs.active=M_ABOUT
    else:
        tabs.active=M_BONFIRE

    while True:
        restore_size()
        if tabs.active not in [M_TABLE,M_HIDDEN_TEST,M_HELP,M_ABOUT]:
            tabs.show_header(s)

        show_page(s,tabs.active)
        tabs.show_footer(s)
        ch=s.getch()
        alt_ch=""
        if ch==27:
            s.nodelay(True)
            next_key=s.getch()
            if next_key!=-1:
                alt_ch=c.keyname(next_key).decode("utf8")
            else:
                alt_ch=""
            if alt_ch=="[":#home and end keys
                for i in range(2):
                    next_key=s.getch()
                    if next_key!=-1:
                        alt_ch+=c.keyname(next_key).decode("utf8")
            s.nodelay(False)
        restore_size()
        tabs.active=react_key(s,tabs.active,ch,alt_ch)
        if tabs.active==M_EXIT:
            break
        if tabs.active==M_WORKSHOP:
            discounts.update_settings()
            discounts.save_settings()
        key=c.keyname(ch).decode("utf-8")
        if key=="KEY_F(10)":
            break
 


c.wrapper(main)