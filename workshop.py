import curses as c

from constants import *
import discounts
import pure_math
import tabs
import utils
import buildings as bs

def show(s):

    s.addstr(1,COL_0,"Discount Type",c.A_BOLD)
    s.addstr(1,COL_1,"Discount Name",c.A_BOLD)
    s.addstr(1,COL_2,"Discount Effect",c.A_BOLD)
    s.addstr(BLOCK_0,COL_0,"Metaphysics")
    s.addstr(BLOCK_1,COL_0,"Huts",c.color_pair(BK_ALT))
    s.addstr(BLOCK_2,COL_0,"Policies")
    s.addstr(BLOCK_3,COL_0,"Other",c.color_pair(BK_ALT))
    for i in range(1,24):
        s.addstr(i,COL_1-1,"|")
        s.addstr(i,COL_2-1,"|")

    for i in range(len(discounts.global_list)):
        selected="X" if discounts.global_idx==i else " "
        s.addstr(BLOCK_0+i,COL_1,chr(65+i)+":("+selected+") "+discounts.global_list[i])
        s.addstr(BLOCK_0+i,COL_2,f"({round(discounts.global_values[i],3)}%)")
    for i in range(len(discounts.huts_list)):
        selected="X" if discounts.huts_idx==i else " "
        postfix="" if i==0 else " Huts"
        s.addstr(BLOCK_1+i,COL_1,chr(71+i)+":("+selected+") "+discounts.huts_list[i]+postfix,c.color_pair(BK_ALT))
        s.addstr(BLOCK_1+i,COL_2,f"({discounts.huts_values[i]}%)",c.color_pair(BK_ALT))
    for i in range(len(discounts.policies_list)):
        selected="X" if discounts.policies_active[i]==1 else " "
        s.addstr(BLOCK_2+i,COL_1,chr(76+i)+":["+selected+"] "+discounts.policies_list[i])
        s.addstr(BLOCK_2+i,COL_2,discounts.policies_desc[i])
    selected="X" if discounts.philosofer==1 else " "
    s.addstr(BLOCK_3+0,COL_1,chr(80)+":["+selected+"] Philosopher leader",c.color_pair(BK_ALT))
    selected="X" if discounts.monrachy==1 else " "
    s.addstr(BLOCK_3+1,COL_1,chr(81)+":["+selected+"] Monarchy",c.color_pair(BK_ALT))
    s.addstr(BLOCK_3+2,COL_1,chr(82)+f":Burned paragon: ",c.color_pair(BK_ALT))
    if discounts.bparagon<9999999:
        edit_box_text=f"{discounts.bparagon}"
    else:
        edit_box_text=pure_math.format_num(discounts.bparagon,FLOAT_KG)
    edit_box_text+=" "*(COL_WIDTH-len(edit_box_text))
    s.addstr(BLOCK_3+2,COL_1+CAP_LEN,edit_box_text,c.color_pair(OTHER_BTN))

    s.addstr(BLOCK_3+3,COL_1,chr(83)+f":Elevator count: ",c.color_pair(BK_ALT))
    edit_box_text=f"{discounts.elevators}"
    edit_box_text+=" "*(COL_WIDTH-len(edit_box_text))
    s.addstr(BLOCK_3+3,COL_1+CAP_LEN,edit_box_text,c.color_pair(OTHER_BTN))

    s.addstr(BLOCK_3+4,COL_1,chr(84)+f":1000 years: ",c.color_pair(BK_ALT))
    edit_box_text=f"{discounts.challenge_1k}"
    edit_box_text+=" "*(COL_WIDTH-len(edit_box_text))
    s.addstr(BLOCK_3+4,COL_1+CAP_LEN,edit_box_text,c.color_pair(OTHER_BTN))

    discount_philosofer_amount=round((1-discounts.get_philosopher_mul())*100.0,2)
    discount_elevators_amount=round((1-discounts.get_space_oil_mul())*100,2)
    discount_1k_amount=round((discounts.get_temporal_press_discount())*100,2)
    s.addstr(BLOCK_3+0,COL_2,f"Order of the Sun (now:-{discount_philosofer_amount}%)",c.color_pair(BK_ALT))
    s.addstr(BLOCK_3+1,COL_2,"Affects philosopher leader",c.color_pair(BK_ALT))
    s.addstr(BLOCK_3+2,COL_2,"Affects philosopher leader",c.color_pair(BK_ALT))
    s.addstr(BLOCK_3+3,COL_2,f"Base space oil (now:-{discount_elevators_amount}%)",c.color_pair(BK_ALT))
    s.addstr(BLOCK_3+4,COL_2,f"Temporal press (now:{discount_1k_amount}%)",c.color_pair(BK_ALT))
    
    #for testing colors
    #s.addstr(BLOCK_3+4,COL_0,"TEST:")
    #for i in range(c.COLORS):
        #s.addstr("TEST ",c.color_pair(i))
    

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
    option=-1
    if m!=None and m[4]&c.BUTTON1_PRESSED and x_mouse >= COL_1+2 and x_mouse <= COL_1+4 and y_mouse>=BLOCK_0 and y_mouse<BLOCK_1:
        option=y_mouse-BLOCK_0
    else:
        option=ord(letter)-65
    if option>=0 and option<len(discounts.global_list):
        discounts.global_idx=option
        return M_WORKSHOP
    if m!=None and m[4]&c.BUTTON1_PRESSED and x_mouse >= COL_1+2 and x_mouse <= COL_1+4 and y_mouse>=BLOCK_1 and y_mouse<BLOCK_2:
        option=y_mouse-BLOCK_1
    else:
        option=ord(letter)-71
    if option>=0 and option<len(discounts.huts_list):
        discounts.huts_idx=option
        return M_WORKSHOP
    if m!=None and m[4]&c.BUTTON1_PRESSED and x_mouse >= COL_1+2 and x_mouse <= COL_1+4 and y_mouse>=BLOCK_2 and y_mouse<BLOCK_3:
        option=y_mouse-BLOCK_2
    else:
        option=ord(letter)-76
    if option>=0 and option<len(discounts.policies_list):
        discounts.policies_active[option]=1 if discounts.policies_active[option]==0 else 0
        return M_WORKSHOP
    if m!=None and m[4]&c.BUTTON1_PRESSED:
        if x_mouse >= COL_1+2 and x_mouse <= COL_1+4 and y_mouse>=BLOCK_3 and y_mouse<BLOCK_3+2:
            option=y_mouse-BLOCK_3
        if x_mouse >= COL_1+CAP_LEN and x_mouse <= COL_1+CAP_LEN+EDIT_WIDTH+1 and y_mouse>=BLOCK_3+2 and y_mouse<BLOCK_3+5:
            option=y_mouse-BLOCK_3
    else:
        option=ord(letter)-80
    if option==0:
        discounts.philosofer=1 if discounts.philosofer==0 else 0
        return M_WORKSHOP
    if option==1:
        discounts.monrachy=1 if discounts.monrachy==0 else 0
        return M_WORKSHOP
    if option==2:
        tabs.active=M_EDIT
        tabs.show_footer(s)
        tabs.active=M_WORKSHOP
        s.keypad(1)
        s.refresh()
        c.curs_set(1)
        win = c.newwin(1,COL_WIDTH,BLOCK_3+2, COL_1+CAP_LEN)
        tb = c.textpad.Textbox(win)
        text = tb.edit(utils.edit_keys)
        c.curs_set(0)
        del win
        if utils.user_cancel:
            utils.user_cancel=False
        else:
            try:
                val=pure_math.parse_num(text.strip())
                if val<0:
                    utils.show_message("Number must be >=0!")
                else:
                    discounts.bparagon=int(val)
            except:
                utils.show_message("Invalid input!")
    if option==3:
        tabs.active=M_EDIT
        tabs.show_footer(s)
        tabs.active=M_WORKSHOP
        s.keypad(1)
        s.refresh()
        c.curs_set(1)
        win = c.newwin(1,COL_WIDTH,BLOCK_3+3, COL_1+CAP_LEN)
        tb = c.textpad.Textbox(win)
        text = tb.edit(utils.edit_keys)
        c.curs_set(0)
        del win
        if utils.user_cancel:
            utils.user_cancel=False
        else:
            try:
                val=pure_math.parse_num(text.strip())
                if val<0:
                    utils.show_message("Number must be >=0!")
                else:
                    discounts.elevators=int(val)
            except:
                utils.show_message("Invalid input!")

        return M_WORKSHOP
    if option==4:
        tabs.active=M_EDIT
        tabs.show_footer(s)
        tabs.active=M_WORKSHOP
        s.keypad(1)
        s.refresh()
        c.curs_set(1)
        win = c.newwin(1,COL_WIDTH,BLOCK_3+4, COL_1+CAP_LEN)
        tb = c.textpad.Textbox(win)
        text = tb.edit(utils.edit_keys)
        c.curs_set(0)
        del win
        if utils.user_cancel:
            utils.user_cancel=False
        else:
            try:
                val=pure_math.parse_num(text.strip())
                if val<0:
                    utils.show_message("Number must be >=0!")
                else:
                    discounts.challenge_1k=int(val)
            except:
                utils.show_message("Invalid input!")

        return M_WORKSHOP
    if letter=='[' and ctrl==True:
        return M_BONFIRE
    if m!=None and m[4]&c.BUTTON3_PRESSED:
        return tabs.get_tab(bs.b_selected)
    return M_WORKSHOP

if __name__=="__main__":
    print("Not main module! ("+__file__+")")