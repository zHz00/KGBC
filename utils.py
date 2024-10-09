import curses as c
def show_message(s):
    c.curs_set(0)
    w=c.newwin(5,60,5,10)
    w.border()
    w.addstr(1,1,s)
    w.addstr(2,15,"<Hit any key to close>")
    w.getch()
    del w

user_cancel=False#there is no way to distinguish Esc from Enter after curses.TextBox.edit(), so i use global variable
def edit_keys(key):
    global user_cancel
    key_txt=c.keyname(key).decode("utf-8")
    if key == 10 or key == 13 or key_txt=="PADENTER":
        key = 7
    if key == 27:
        user_cancel=True
        key = 7
    if key == c.KEY_MOUSE:
        m=c.getmouse()
        if m[4]&c.BUTTON3_PRESSED:
            user_cancel=True
            key = 7
    return key