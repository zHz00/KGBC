import json
import curses as c

from constants import *
import utils
import discounts
import table
import buildings as bs
import pure_math
import copy

tests_list=[]
page=0
PAGE_SIZE=6

TESTS_FILE="kgbc_tests.txt"

kg_defaults={
    'name':"dummy",
    'i':1,
    'idx':0,
    'huts_idx':0,
    'active':[0,0,0,0],
    'philosopher':0,
    'monarchy':0,
    'bparagon':0,
    'elevators':0,
    'challenge_1k':0,
    'result':[10.0],
    'show_disclaimer':1,
    'theme':0
}

def save_tests(file:str,t_list)->None:
    f=open(file,"w",encoding="utf-8")
    json.dump(t_list,f,indent=2)
    f.close()


def load_tests(file:str)->None:
    try:
        f=open(file,"r",encoding="utf-8")
    except:
        return [kg_defaults]
        
    tests_list_raw=None
    tests_list_raw=json.load(f)
    tests_list_ordered=[]
    f.close()
    for t in tests_list_raw:
            test=dict()
            test["name"]=t["name"]
            test["i"]=t["i"]
            test['idx']=t["idx"]
            test["huts_idx"]=t["huts_idx"]
            test["active"]=copy.deepcopy(t["active"])
            test["philosopher"]=t["philosopher"]
            test["monarchy"]=t["monarchy"]
            test["bparagon"]=t["bparagon"]
            test["elevators"]=t["elevators"]
            if "challenge_1k" not in t.keys():
                test["challenge_1k"]=0
            else:
                test["challenge_1k"]=t["challenge_1k"]
            tests_list_ordered.append(test)
            test["result"]=copy.deepcopy(t["result"])
            if "show_disclaimer" not in t.keys():
                test["show_disclaimer"]=1
            else:
                test["show_disclaimer"]=t["show_disclaimer"]
            if "theme" not in t.keys():
                test["theme"]=1
            else:
                test["theme"]=t["theme"]
    return tests_list_ordered

def show_hidden_test(s):
    global tests_list

    s.clear()
    if page==0:
        tests_list=load_tests(TESTS_FILE)
        s.clear()
    n_start=page*PAGE_SIZE
    for n in range(n_start,n_start+PAGE_SIZE):
        if n>=len(tests_list):
            break
        print_header(s,n,len(tests_list),tests_list[n]["name"],tests_list[n]["i"])
        s.refresh()
        print_test(s,tests_list[n])
        print_result(s,tests_list[n])



def make_test(b,i):
    global tests
    test=dict()
    if b!=None:
        test["name"]=b["Name"]
    else:
        test["name"]="dummy"
    test["i"]=i
    test['idx']=discounts.global_idx
    test["huts_idx"]=discounts.huts_idx
    test["active"]=copy.deepcopy(discounts.policies_active)
    test["philosopher"]=discounts.philosofer
    test["monarchy"]=discounts.monrachy
    test["bparagon"]=discounts.bparagon
    test["elevators"]=discounts.elevators
    test["challenge_1k"]=discounts.challenge_1k
    test["show_disclaimer"]=discounts.show_disclaimer
    test["theme"]=discounts.theme
    if b!=None:
        test["result"]=table.calc_recipe(b,i)
    else:
        test["result"]=[0.0]
    return test

def print_header(s,n, total, name, i):
    h=f"{n+1}/{total}. {name}#{i+1}"
    #left="="*(78-len(h))
    s.addstr(h,c.color_pair(BK)|c.A_BOLD)

def print_test(s,t:dict):
    s.addstr("|Global:"+discounts.global_list[t["idx"]]+"|Huts:"+discounts.huts_list[t["huts_idx"]]+"|\n")
    for i in range(len(t["active"])):
        s.addstr(discounts.policies_list_short[i]+f":{t['active'][i]}|")
    if t["philosopher"]==1:
        s.addstr("Phil:1|")
    else:
        s.addstr("Phil:0|")
    if t["monarchy"]==1:
        s.addstr("Mon:1|")
    else:
        s.addstr("Mon:0|")
    s.addstr(f"BP:{pure_math.format_num(t['bparagon'],FLOAT_KG,fill=False)}|Elev:{pure_math.format_num(t['elevators'],FLOAT_KG,fill=False)}|1k:{pure_math.format_num(t['challenge_1k'],FLOAT_KG,fill=False)}\n")

def print_result(s,t):

    found=False
    for b in bs.buildings:
        if b["Name"]==t['name']:
            found=True
            discounts.load_settings(t)
            values=table.calc_recipe(b,t['i'])
            flag_ok=True
            for i in range(len(values)):
                if values[i]==t['result'][i]:#for overflow
                    continue
                if abs(values[i]-t['result'][i])<1e-3:#for floats
                    continue
                flag_ok=False
            if flag_ok:
                t['passed']=True
                style=c.color_pair(TEST_OK)
            else:
                t['passed']=False
                style=c.color_pair(TEST_FAIL)
            for i in range(len(t['result'])):
                s.addstr(pure_math.format_num(t['result'][i],FLOAT_KG)+"|",style)
            s.addstr("<-REF\n")
            for i in range(len(values)):
                s.addstr(pure_math.format_num(values[i],FLOAT_KG)+"|",style)
            s.addstr("<-CUR")
            s.refresh()
            (y,x)=s.getyx()
            if y!=24:
                s.addstr("\n")
            if flag_ok:
                return 1
            else:
                return 0
    if found==False:
        s.addstr("NOT FOUND",c.color_pair(TEST_FAIL))
        s.addstr("\n"+("="*78)+"\n")
        return 0

def react(s,ch,m,alt_ch):
    global page
    if ch==ord(" "):
        page+=1
    if ch==27:
        return M_BONFIRE
    if page*PAGE_SIZE>=len(tests_list):
        successful=0
        for t in tests_list:
            if 'passed' in t and t['passed']==True:
                successful+=1
        utils.show_message(f"Total: {len(tests_list)}, OK:{successful}")
        discounts.load_settings(discounts.settings[0])
        page=0
        return M_BONFIRE
    return M_HIDDEN_TEST

if __name__=="__main__":
    print("Not main module! ("+__file__+")")