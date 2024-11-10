import curses as c

from constants import *
import tabs
import utils
import discounts

PAGE_SIZE=18
W=58
BEGIN_Y=4
BEGIN_X=11
page=M_BONFIRE
contents_w=None
contents_lines=[]
w=None
line=-1


def center(s,W):
    return int((W-len(s))/2)

def show(s):
    global contents_lines,line
    c.curs_set(0)
    w=c.newwin(PAGE_SIZE+2,W+2,BEGIN_Y-1,BEGIN_X-1)
    w.border()
    header=" Help: "+tabs.get_tab_name(page)+" "
    x=center(header,W+2)
    w.addstr(0,x,header)
    contents_w=c.newwin(PAGE_SIZE,W,BEGIN_Y,BEGIN_X)
    if line==-1:
        try:
            file=open("help/"+tabs.get_tab_name(page)+".md","r")
        except:
            utils.show_message("No help file found! -- "+tabs.get_tab_name(page))
            return
        contents_lines=file.readlines()
        file.close()
        for i in range(len(contents_lines)):
            contents_lines[i]=contents_lines[i].replace("\t"," ").replace("\n","").replace("\r","")
            #contents_lines[i]=contents_lines[i][:W-1]
        line=0
    #for i in range(line,line+PAGE_SIZE):
        #if i<len(contents_lines):
            #contents_w.addstr(i-line,0,contents_lines[i].rstrip())
    for i in range(line,line+PAGE_SIZE):
        if i<len(contents_lines):
            contents_w.move(i-line,0)
            prev_ch=''
            ln=contents_lines[i]
            mode=HELP_NORMAL
            ch_counter=0
            if ln.startswith("**Philosopher"):
                ln=ln
            for ch in range(len(contents_lines[i])):
                if ln[ch]=='\\' and prev_ch!='\\':
                    prev_ch=ln[ch]
                    continue
                if ln[ch]=='*' and prev_ch!='\\' and mode==HELP_NORMAL:
                    mode=HELP_BOLD
                    prev_ch=ln[ch]
                    continue
                if ln[ch]=='*' and prev_ch!='\\' and prev_ch!='*' and mode==HELP_BOLD:
                    mode=HELP_NORMAL
                    prev_ch=ln[ch]
                    continue
                if ln[ch]=='_' and prev_ch!='\\' and mode==HELP_NORMAL:
                    mode=HELP_NAME
                    prev_ch=ln[ch]
                    continue
                if ln[ch]=='_' and prev_ch!='\\' and prev_ch!='_' and mode==HELP_NAME:
                    mode=HELP_NORMAL
                    prev_ch=ln[ch]
                    continue
                if ln[ch]=='*' and prev_ch=='*' and mode in [HELP_NORMAL,HELP_BOLD]:
                    mode=HELP_ITALIC
                    prev_ch=ln[ch]
                    continue
                if ln[ch]=='*' and prev_ch=='*' and mode==HELP_ITALIC:
                    mode=HELP_NORMAL
                    prev_ch=ln[ch]
                    continue
                if ln[ch]=='*' and prev_ch!='\\':#we have asterisk that was not caught before. probably this is **. Skipping
                    prev_ch=ln[ch]
                    continue


                if ln[ch]=='#' and ch==0:
                    mode=HELP_HEADER
                    prev_ch=ln[ch]
                    continue
                contents_w.addstr(ln[ch],c.color_pair(mode))
                ch_counter+=1
                prev_ch=ln[ch]
    if len(contents_lines)>0:
        percentage=int((line)/(len(contents_lines)-PAGE_SIZE)*100.0)
    else:
        percentage=100
    footer=f"{percentage}%"
    x=center(footer,W+2)
    w.addstr(PAGE_SIZE+1,x,footer)
    w.refresh()
    contents_w.refresh()

def react(s,ch,m,alt_ch):
    global page,w,contents_w,line
    if line==-1:
        ch=27#exit if file not found
    key=c.keyname(ch).decode("utf-8")
    key=key.upper()
    if m!=None:
        if m[4]&c.BUTTON4_PRESSED:
            if line>0:
                line-=1
        if m[4]&0x200000:
            if line<len(contents_lines)-PAGE_SIZE:
                line+=1
        if m[4]&c.BUTTON3_PRESSED:
            ch=27
    if key=="KEY_PPAGE":
        line-=PAGE_SIZE
        if line<0:
            line=0
    if key=="KEY_NPAGE":
        if line<len(contents_lines)-PAGE_SIZE:
            line+=PAGE_SIZE
        if line>=len(contents_lines)-PAGE_SIZE:
            line=len(contents_lines)-PAGE_SIZE
    if key=="KEY_UP":
        if line>0:
            line-=1
    if key=="KEY_DOWN":
        if line<len(contents_lines)-PAGE_SIZE:
            line+=1
    if key=="KEY_HOME" or alt_ch=="[H" or alt_ch=="[1~":
        line=0
    if key=="KEY_END" or key=="KEY_A1" or alt_ch=="[4~":
        line=len(contents_lines)-PAGE_SIZE
    if key=="KEY_F(7)" and page==M_ABOUT:
        if discounts.show_disclaimer==1:
            discounts.show_disclaimer=0
        else:
            discounts.show_disclaimer=1
        discounts.update_settings()
        discounts.save_settings()
    if (ch==27 and page!=M_ABOUT) or (key=="KEY_F(4)" and page==M_ABOUT):
        line=-1
        del w
        w=None
        del contents_w
        contents_w=None
        if page==M_ABOUT:
            return M_BONFIRE
        else:
            return page
    if page==M_ABOUT:
        return M_ABOUT
    else:
        return M_HELP