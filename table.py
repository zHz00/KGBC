import curses as c

import discounts
from constants import *
import pure_math
import tabs
import utils
import buildings as bs
import tests

table_start=0
table_cursor=0
table_sel_b=-1
table_sel_e=-1

TABLE_MAX=20

def move_down():
    global table_cursor,table_start
    if table_cursor<TABLE_MAX-1:#similar to KEY_DOWN
        table_cursor+=1
    else:
        table_start+=1

def order_sel():
    global table_sel_b,table_sel_e
    if table_sel_e<table_sel_b:
        tmp=table_sel_b
        table_sel_b=table_sel_e
        table_sel_e=tmp

def calc_sum_old_style(b,beg,end):
    sum=[0.0]*len(b["Recipe"])
    for i in range(beg,end+1):
        values=calc_recipe(b,i)
        sum=list(map(add_component,sum,values))
    return sum

def calc_sum_new_style(b,beg,end):
    if beg==end:
        return calc_recipe(b,beg)#not for speed but for summing near 1e308
    sum=[0.0]*len(b["Recipe"])
    v1=calc_recipe(b,beg)
    v2=calc_recipe(b,end)
    ratios=get_ratios(b)
    for i in range(len(sum)):
        if v1[i]==OVERFLOW or v2[i]==OVERFLOW:
            sum[i]=OVERFLOW
        else:
            try:
                sum[i]=(v1[i]-v2[i])/(1-ratios[i])
            except OverflowError:
                sum[i]=OVERFLOW
    sum=list(map(add_component,sum,v2))#adding last
    return sum


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

def get_ratios(b):
    (recipe,mul,mul_gold,mul_oil)=discounts.base_discount(b)
    ratio=b["Ratio"]+discounts.get_discount(b)
    ratio_oil=1.05
    ratio_starchart=1.35*ratio
    ratios=[]
    for key,value in recipe.items():
        if key=="oil" and discounts.using_oil_ratio(b):
            ratios.append(ratio_oil)
            continue
        if key=="starchart" and discounts.using_starchart_ratio(b):
            ratios.append(ratio_starchart)
            continue
        ratios.append(ratio)
    return ratios

def calc_recipe(b,i):#i begins with zero for first building!
    (recipe,mul,mul_gold,mul_oil)=discounts.base_discount(b)
    ratio=b["Ratio"]+discounts.get_discount(b)
    ratio_oil=1.05
    ratio_starchart=1.35*ratio
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
    ratio_starchart=1.35*ratio
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
        ratio_info+=f" ({round(ratio_starchart,3)} for starchart)"

    base_discount_info=""
    if mul<1.0:
        base_discount_info+=f"Base discount: -{round((1-mul)*100,1)}%"
    if mul_gold<1.0:
        if len(base_discount_info)>0:
            base_discount_info+="; Gold: -"
        else:
            base_discount_info+="Gold base discount: -"
        base_discount_info+=f"{round((1-mul*mul_gold)*100,1)}%"
    if mul_oil<1.0:
        if len(base_discount_info)>0:
            base_discount_info+="; "
        base_discount_info+=f"Oil base discount: -{round((1-mul_oil)*100,2)}%"
    
    #make header

    s.clear()

    s.addstr(0,0,info,c.color_pair(BUILDING_HEADER))
    s.chgat(c.color_pair(BUILDING_HEADER))
    s.addstr(1,0,ratio_info,c.color_pair(RATIO_INFO))
    s.chgat(c.color_pair(RATIO_INFO))
    s.addstr(1,40,base_discount_info,c.color_pair(RATIO_INFO))
    s.addstr(0,0,"[",c.color_pair(INACTIVE_TAB)|c.A_BOLD)
    s.addstr(0,1,"<-",c.color_pair(ATTENTION_INACTIVE))
    s.addstr(0,3,"]",c.color_pair(INACTIVE_TAB)|c.A_BOLD)
    
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
    s.addstr(0,68,sel_hint,c.color_pair(ATTENTION_INACTIVE))

    style=c.color_pair(BK)|c.A_BOLD
    s.addstr(2,0,"#"+(" "*(COL_T_0-1))+"|",style)
    for key,value in recipe.items():
        s.addstr(2,COL_T_0+recipe_n*COL_WIDTH,"|"+key,style)
        recipe_n+=1
    s.addstr(2,COL_T_0+recipe_n*COL_WIDTH,"|",style)
    for i in range(table_start,TABLE_MAX+table_start):
        id=f"{i+1}"
        if b["Name"] in color_unlocking_list.keys():
            if i+1==color_unlocking_list[b["Name"]]:
                id+="*"
        id+=" "*(COL_T_0-len(id))#filler
        style=0
        inside_selection=False
        if i>=real_sel_b and i<=real_sel_e:
            inside_selection=True
        if inside_selection:
            if (i-table_start)==table_cursor:
                style=c.color_pair(BK_CURSOR_SEL)
            else:
                style=c.color_pair(BK_SEL)
        else:
            if (i-table_start)==table_cursor:
                style=c.color_pair(BK_CURSOR)
            else:
                style=c.color_pair(BK)
        s.addstr(3+(i-table_start),0,id,style)
        recipe_n=0
        values=calc_recipe(b,i)
        for j in range(len(values)):
            if values[j]==OVERFLOW:
                s.addstr(3+(i-table_start),COL_T_0+j*COL_WIDTH,"|[OVERFLOW] ",style)
            else:
                s.addstr(3+(i-table_start),COL_T_0+j*COL_WIDTH,"|"+pure_math.format_num(values[j],float_mode),style)
        s.addstr("|",style)
        if real_sel_b!=-1 and real_sel_e!=-1:#counting sum
            summed=real_sel_e-real_sel_b+1
            summed_str=""
            if summed<=99:
                summed_str="("+str(summed)+")"
            else:
                if summed<=999:
                    summed_str=":"+str(summed)
                else:
                    summed_str=str(summed)
            s.addstr(23,0,"SUM"+summed_str,c.color_pair(ATTENTION))
            s.addstr(23,COL_T_0,"|",c.color_pair(ATTENTION))
            sum=calc_sum_new_style(b,real_sel_b,real_sel_e)
            recipe_n=0
            for i in range(len(sum)):
                s.addstr(23,COL_T_0+i*COL_WIDTH,"|"+("[OVERFLOW] " if sum[i]==OVERFLOW else pure_math.format_num(sum[i],float_mode)),c.color_pair(ATTENTION))
            s.addstr("|",c.color_pair(ATTENTION))
            """sum2=calc_sum_old_style(b,real_sel_b,real_sel_e)

            fail=False
            for i in range(len(sum)):
                if sum2[i]-sum[i]>1e-3:
                    fail=True
            if fail==True:
                utils.show_message("sum2!=sum1 !")"""



def react(s,ch,m,alt_ch):
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
    if x_mouse!=0 or y_mouse!=0:
        if y_mouse==0 and x_mouse in [0,1,2,3]:
            return tabs.get_tab(bs.b_selected)
        if y_mouse-3<TABLE_MAX and y_mouse>=3 and m[4]&c.BUTTON1_PRESSED:
            table_cursor=y_mouse-3
        if y_mouse<3 and m[4]&c.BUTTON1_PRESSED:
            table_sel_b=-1
            table_sel_e=-1
        if y_mouse-3<TABLE_MAX and y_mouse>=3 and (m[4]&c.BUTTON1_DOUBLE_CLICKED or m[4]&c.BUTTON2_PRESSED):
            if table_sel_b==-1 or (table_sel_b!=-1 and table_sel_e!=-1):#selection had zero or two coordinates: resetting
                table_cursor=y_mouse-3
                table_sel_b=(y_mouse-3)+table_start
                table_sel_e=-1
            else:
                table_cursor=y_mouse-3
                table_sel_e=(y_mouse-3)+table_start
    if letter=="+":
        tests.tests_list.append(tests.make_test(bs.b_selected,table_start+table_cursor))
        s.move(0,0)
        tests.print_result(s,tests.tests_list[-1])
        utils.show_message(f"Test added to list. Total: {len(tests.tests_list)}")
    if letter=="S":
        if len(tests.tests_list)==0:
            utils.show_message("Tests list is empty! Can't save.")
        else:
            tests.save_tests(tests.TESTS_FILE,tests.tests_list)
            utils.show_message(f"Tests list saved. Total tests: {len(tests.tests_list)}")
    if key=="KEY_PPAGE":
        table_start-=TABLE_MAX
        if table_start<0:
            table_start=0
    if key=="KEY_NPAGE":
        table_start+=TABLE_MAX
    if key=="KEY_UP":
        if table_cursor>0:
            table_cursor-=1
        else:
            table_start-=1
            if table_start<0:
                table_start=0
    if key=="KEY_DOWN":
        move_down()
    if key=="KEY_HOME":
        table_start=0
        table_cursor=0
    if key=="KEY_END":
        table_start+=TABLE_MAX*5#100 by default
    if key=="KEY_IC":#insert
        if table_sel_b==-1:#no selection
            table_sel_b=table_cursor+table_start
            table_sel_e=table_sel_b
            move_down()
            return M_TABLE
        if (table_sel_b!=-1 and table_sel_e==-1):#continue selection
            table_sel_e=table_cursor+table_start
            order_sel()

        #we're in the end of existing selection
        order_sel()

        if table_cursor+table_start == table_sel_e:#remove selection from last, not moving cursor
            if table_sel_e==table_sel_b:#only one line
                table_sel_b=table_sel_e=-1
                return M_TABLE
            table_sel_e=table_cursor+table_start-1
            return M_TABLE
        if table_cursor+table_start == table_sel_e+1:
            table_sel_e=table_cursor+table_start
            move_down()
            return M_TABLE
        
        if table_cursor+table_start == table_sel_b-1:
            table_sel_b=table_cursor+table_start
            return M_TABLE

        if table_cursor+table_start==table_sel_b:#reduce selection
            table_sel_b+=1
            move_down()
            return M_TABLE

        #now we have case with existing selection
        return M_TABLE

    if letter=='I' and ctrl==True:#worked on windows for tab
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
    if letter=="-" or key=="PADMINUS":
        table_sel_b=-1
        table_sel_e=-1
    return M_TABLE

if __name__=="__main__":
    print("Not main module! ("+__file__+")")