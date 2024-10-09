import json
import curses as c

from constants import *
import utils
import discounts
import table
import buildings as bs
import pure_math

tests_list=[]

def show_hidden_test(s):
    global tests
    f=open("kgbc_tests.txt","r",encoding="utf-8")
    tests_list=None
    tests_list=json.load(f)
    f.close()
    s.clear()
    i=1
    successful=0
    for t in tests_list:
        s.addstr(f"{i}.",c.color_pair(ATTENTION)|c.A_BOLD)
        print_test(s,t)
        successful+=print_result(s,t)
        if i%5==0:
            s.getch()
            s.clear()
        i+=1
    s.getch()
    utils.show_message(f"Total: {i-1}, OK:{successful}")

    kg_test={
    'idx':0,
    'huts_idx':0,
    'active':[0,0,0,0],
    'philosopher':0,
    'monarchy':0,
    'bparagon':0,
    'elevators':0,
    'name':"Catnip Field",
    'i':1,
    'result':[10.0]
}

def make_test(b,i):
    global tests
    test=dict()
    test['idx']=discounts.global_idx
    test["huts_idx"]=discounts.huts_idx
    test["active"]=discounts.policies_active
    test["philosopher"]=discounts.philosofer
    test["monarchy"]=discounts.monrachy
    test["bparagon"]=discounts.bparagon
    test["elevators"]=discounts.elevators
    test["name"]=b["Name"]
    test["i"]=i
    test["result"]=table.calc_recipe(b,i)
    tests_list.append(test)

def print_test(s,t:dict):
    s.addstr(f"{t['name']}#{t['i']+1}|Global:")
    s.addstr(discounts.global_list[t["idx"]]+"|Huts:"+discounts.huts_list[t["huts_idx"]]+"|")
    for i in range(len(t["active"])):
        s.addstr(discounts.policies_list[i]+f":{t['active'][i]}|")
    if t["philosopher"]==1:
        s.addstr("Philosopher:1|")
    else:
        s.addstr("Philosopher:0|")
    if t["monarchy"]==1:
        s.addstr("Monarchy:1|")
    else:
        s.addstr("Monarchy:0|")
    s.addstr(f"BP:{t['bparagon']}|Elevators:{t['elevators']}\n")

def print_result(s,t):

    found=False
    for b in bs.buildings:
        if b["Name"]==t['name']:
            found=True
            discounts.global_idx=t['idx']
            discounts.huts_idx=t['huts_idx']
            discounts.policies_active=t['active']
            discounts.philosofer=t['philosopher']
            discounts.monrachy=t['monarchy']
            discounts.bparagon=t['bparagon']
            discounts.elevators=t['elevators']
            values=table.calc_recipe(b,t['i'])
            flag_ok=True
            for i in range(len(values)):
                if values[i]==t['result'][i]:#for overflow
                    continue
                if abs(values[i]-t['result'][i])<1e-3:#for floats
                    continue
                flag_ok=False
            if flag_ok:
                style=c.color_pair(TEST_OK)|c.A_BOLD
            else:
                style=c.color_pair(TEST_FAIL)|c.A_BOLD
            for i in range(len(t['result'])):
                s.addstr(pure_math.format_num(t['result'][i],FLOAT_KG)+"|",style)
            s.addstr("<-REF\n")
            for i in range(len(values)):
                s.addstr(pure_math.format_num(values[i],FLOAT_KG)+"|",style)
            s.refresh()
            s.addstr("<-CUR\n"+("="*78))
            (y,x)=s.getyx()
            if y!=24:
                s.addstr("\n")
            if flag_ok:
                return 1
            else:
                return 0
    if found==False:
        style=c.color_pair(TEST_FAIL)|c.A_BOLD
        s.addstr("NOT FOUND",style)
        s.addstr("\n"+("="*78)+"\n")
        return 0