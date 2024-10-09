import curses as c

import discounts
from constants import *
import pure_math
import tabs
import utils
import buildings as bs
import json
import tests

table_start=0
table_cursor=0
table_sel_b=-1
table_sel_e=-1

float_mode=FLOAT_KG

color_unlocking_list={
    "Mint":24,
    "Satellite":24,
    "Academy":68,
    "Hydraulic Fracturer":10,
    "Research Vessel":20,
    "Warehouse":10,
    "Oil Well":73,
    "Unicorn Utopia":1,
    "Mine":92,
    "Brewery":10,
    "Chronocontrol":1,
    "Data Center":100,
    "Cryostation":10,
    "AI Core":5,
    "Factory":20,
    "Catnip Fiels":56,
    "Spice Refinery":10
}

def add_component(a,b):
    if a==OVERFLOW or b==OVERFLOW:
        return OVERFLOW
    return a+b

def calc_recipe(b,i):
    (recipe,mul,mul_gold,mul_oil)=discounts.base_discount(b)
    ratio=b["Ratio"]+discounts.get_discount(b)
    ratio_oil=1.05
    ratio_starchart=1.35
    values=[]
    for key,value in recipe.items():
            try:
                if key=="oil" and discounts.using_oil_ratio(b):
                    values.append(value*(ratio_oil**i))
                else:
                    if key=="starchart" and discounts.using_starchart_ratio(b):
                        values.append(value*(ratio_starchart**i))
                    else:
                        values.append(value*(ratio**i))
            except OverflowError:
                values.append(OVERFLOW)
    return values

def reset_table():
    global table_start
    global table_cursor
    global table_sel_b
    global table_sel_e

    table_start=0
    table_cursor=0
    table_sel_b=-1
    table_sel_e=-1

def show(s,b):
    ratio=b["Ratio"]+discounts.get_discount(b)
    ratio_oil=1.05
    ratio_starchart=1.35
    (recipe,mul,mul_gold,mul_oil)=discounts.base_discount(b)
    name="=== "+b["Name"]+" ==="
    space=" "*int((80-len(name))/2)
    info=space+name+space
    ratio_info=f"Ratio: {round(ratio,3)}"
    if discounts.get_discount(b)!=0:
        ratio_info+=f" (default: {b['Ratio']})"
    if discounts.using_oil_ratio(b):
        ratio_info+=f" ({ratio_oil} for oil)"
    if discounts.using_starchart_ratio(b):
        ratio_info+=f" ({ratio_starchart} for starchart)"

    base_discount_info=""
    if mul<1.0:
        base_discount_info+=f"Base discount: -{round((1-mul)*100,1)}%"
    if mul_gold<1.0:
        base_discount_info+=f"Gold base discount: -{int(round((1-mul_gold)*100,0))}%"
    if mul_oil<1.0:
        base_discount_info+=f"Oil base discount: -{round((1-mul_oil)*100,2)}%"
    
    #make header

    s.clear()

    s.addstr(0,0,info,c.color_pair(BUILDING_HEADER)|c.A_BOLD)
    s.chgat(c.color_pair(INACTIVE_TAB))
    s.addstr(1,0,ratio_info,c.color_pair(INACTIVE_TAB))
    s.chgat(c.color_pair(INACTIVE_TAB))
    s.addstr(1,40,base_discount_info,c.color_pair(INACTIVE_TAB))

    id_len=4
    recipe_n=0

    SEL_NONE=0
    SEL_NOW=1
    SEL_ENDED=2

    #selection of range
    real_sel_b=-1
    real_sel_e=-1
    sel_mode=SEL_NONE
    if table_sel_b!=-1 and table_sel_e==-1:
        real_sel_b=table_sel_b
        real_sel_e=table_cursor+table_start
        sel_mode=SEL_NOW
    if table_sel_b!=-1 and table_sel_e!=-1:
        real_sel_b=table_sel_b
        real_sel_e=table_sel_e
        sel_mode=SEL_ENDED
    if real_sel_b>real_sel_e:
        tmp=real_sel_b
        real_sel_b=real_sel_e
        real_sel_e=tmp

    sel_hint=""
    if sel_mode==SEL_NOW:
        sel_hint="SELECT"
    if sel_mode==SEL_ENDED:
        sel_hint=f"SUM OF {real_sel_e-real_sel_b+1}"
    s.addstr(0,68,sel_hint,c.color_pair(ATTENTION_INACTIVE)|c.A_BOLD)

    style=c.color_pair(BK)|c.A_BOLD
    s.addstr(2,0,"#   |",style)
    for key,value in recipe.items():
        s.addstr(2,4+recipe_n*COL_WIDTH,"|"+key,style)
        recipe_n+=1
    s.addstr(2,4+recipe_n*COL_WIDTH,"|",style)
    for i in range(table_start,TABLE_MAX+table_start):
        id=f"{i+1}"
        if b["Name"] in color_unlocking_list.keys():
            if i+1==color_unlocking_list[b["Name"]]:
                id+="*"
        id+=" "*(id_len-len(id))#filler
        style=0
        inside_selection=False
        if i>=real_sel_b and i<=real_sel_e:
            inside_selection=True
        if inside_selection:
            if (i-table_start)==table_cursor:
                style=c.color_pair(BK_CUR_SEL)|c.A_BOLD
            else:
                style=c.color_pair(BK_SEL)+c.A_BOLD
        else:
            if (i-table_start)==table_cursor:
                style=c.color_pair(BK_CUR)
            else:
                style=c.color_pair(BK)
        s.addstr(3+(i-table_start),0,id,style)
        recipe_n=0
        values=calc_recipe(b,i)
        for j in range(len(values)):
            if values[j]==OVERFLOW:
                s.addstr(3+(i-table_start),4+j*COL_WIDTH,"|[OVERFLOW] ",style)
            else:
                s.addstr(3+(i-table_start),4+j*COL_WIDTH,"|"+pure_math.format_num(values[j],float_mode),style)
        s.addstr("|",style)
        if real_sel_b!=-1 and real_sel_e!=-1:#counting sum
            s.addstr(23,0,"SUM:|",c.color_pair(ATTENTION)|c.A_BOLD)
            sum=[0.0]*len(recipe)
            for i in range(real_sel_b,real_sel_e+1):
                values=calc_recipe(b,i)
                sum=list(map(add_component,sum,values))
            recipe_n=0
            for i in range(len(sum)):
                s.addstr(23,4+i*COL_WIDTH,"|"+("[OVERFLOW] " if sum[i]==OVERFLOW else pure_math.format_num(sum[i],float_mode)),c.color_pair(ATTENTION)|c.A_BOLD)

def react(s,ch,m):
    global table_cursor
    global table_sel_b
    global table_sel_e
    global table_start
    global float_mode

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
    if m!=None:
        if m[4]&c.BUTTON4_PRESSED:
            table_start-=1
            if table_start<0:
                table_start=0
        if m[4]&0x200000:
            table_start+=1
        if m[4]&c.BUTTON3_PRESSED:
            return tabs.get_tab(bs.b_selected)
    if x_mouse!=0 and y_mouse!=0:
        if y_mouse-3<TABLE_MAX and y_mouse>=3 and m[4]&c.BUTTON1_PRESSED:
            table_cursor=y_mouse-3
        if y_mouse<3 and m[4]&c.BUTTON1_PRESSED:
            table_sel_b=-1
            table_sel_e=-1
        if y_mouse-3<TABLE_MAX and y_mouse>=3 and m[4]&c.BUTTON1_DOUBLE_CLICKED:
            if table_sel_b==-1 or (table_sel_b!=-1 and table_sel_e!=-1):#selection had zero or two coordinates: resetting
                table_sel_b=(y_mouse-3)+table_start
                table_sel_e=-1
            else:
                table_sel_e=(y_mouse-3)+table_start
    if letter=="+":
        tests.make_test(bs.b_selected,table_start+table_cursor)
        utils.show_message("OK")
    if letter=="S":
        f=open("kgbc_tests.txt","w",encoding="utf-8")
        json.dump(tests.tests_list,f)
        f.close()
        utils.show_message("SAVED")
    if key=="KEY_PPAGE":
        table_start-=20
        if table_start<0:
            table_start=0
    if key=="KEY_NPAGE":
        table_start+=20
    if key=="KEY_UP":
        if table_cursor>0:
            table_cursor-=1
        else:
            table_start-=1
            if table_start<0:
                table_start=0
    if key=="KEY_DOWN":
        if table_cursor<TABLE_MAX-1:
            table_cursor+=1
        else:
            table_start+=1
    if key=="KEY_HOME":
        table_start=0
        table_cursor=0
    if letter=='I' and ctrl==True:#workd on windows for tab
        if float_mode==FLOAT_KG:
            float_mode=FLOAT_SCI
        else:
            float_mode=FLOAT_KG
    if letter=='[' and ctrl==True:
        return tabs.get_tab(bs.b_selected)
    if (letter=="[" and ctrl==False) or letter=="]":
        if table_sel_b==-1 or (table_sel_b!=-1 and table_sel_e!=-1):#selection had zero or two coordinates: resetting
            table_sel_b=table_cursor+table_start
            table_sel_e=-1
        else:
            table_sel_e=table_cursor+table_start
    if letter=="-":
        table_sel_b=-1
        table_sel_e=-1
    return M_TABLE