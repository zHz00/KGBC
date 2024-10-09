import curses as c
def show_message(s,noans=False):
    W=60
    c.curs_set(0)
    w=c.newwin(7,W,10,10)
    w.border()
    begin=int((W-len(s))/2)
    if begin<0:
        begin=0
    w.addstr(1,begin,s)
    hint="<Hit any key to close>"
    w.addstr(4,int((W-len(hint))/2),hint)
    if noans==False:
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

if __name__=="__main__":
    print("Not main module! ("+__file__+")")