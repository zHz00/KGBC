import curses as c
import sqlite3 as sl
import json
import os

try:
    import esprima
    esprima_absent=False
except ModuleNotFoundError:
    esprima_absent=True

from constants import *
import tabs
import utils
import pure_math


folder=""
log=None
groups_names=[]
groups_contents=[]

test_value=0
test_stripe=0
test_effect=0
test_limit=0

def get_label(label):
    jsfile="../res/i18n/en.json"
    t=open(folder+jsfile,"r")
    #s=t.read()
    #t.close()
    j=json.load(t)
    return j[label]

def find_property(e_object,name):
    for p in e_object.properties:
        if p.key.name==name:
            return p
    return None

def get_property_value(e_object,name):
    p=find_property(e_object,name)
    if p==None:
        return "NotFound"
    return p.value.value

def get_materials(b):
    p_dict=dict()
    prices=find_property(b,"prices")
    if prices==None:
        prices=find_property(b,"embassyPrices")
    for p in prices.value.elements:
        p_name=p.properties[0].value.value
        p_count=p.properties[1].value.value
        p_dict[p_name]=p_count
    return p_dict

def get_groups():
    global groups_names,groups_contents
    jsfile="buildings.js"
    cname="classes.managers.BuildingsManager"
    t=open(folder+jsfile,"r")
    s=t.read()
    t.close()
    p=esprima.parseScript(s)

    group_class=None
    for dojo_declare in p.body:
        if dojo_declare.expression.arguments[0].value==cname:
            group_class=dojo_declare.expression.arguments[2]

    groups_names=[]
    groups_contents=[]
    groups_property=find_property(group_class,"buildingGroups")
    groups_list=groups_property.value.elements
    for group in groups_list:
        groups_names.append(get_property_value(group,"name"))
        contents=find_property(group,"buildings").value.elements
        groups_contents.append([])
        for e in contents:
            groups_contents[-1].append(e.value)


def get_group_name(b_name:str):
    if b_name!="":
        b_name=b_name
    for i in range(len(groups_names)):
        for g in groups_contents[i]:
            if g==b_name:
                return groups_names[i]
    return "NONE"

def get_planet_list():
    jsfile="space.js"
    cname="classes.managers.SpaceManager"

    t=open(folder+jsfile,"r")
    s=t.read()
    t.close()
    p=esprima.parseScript(s)

    building_class=None
    for dojo_declare in p.body:
        if dojo_declare.expression.arguments[0].value==cname:
            building_class=dojo_declare.expression.arguments[2]

    planet_names=[]
    planets_property=find_property(building_class,"planets")
    planets_list=planets_property.value.elements
    for planet in planets_list:
        planet_names.append(get_property_value(planet,"name"))

    return planet_names

kg_db=[]

def parse_space(cat,jsfile,cname):
    planet_names=get_planet_list()
    for planet in planet_names:
        log.addstr("Parsing "+planet+"...|")
        log.refresh()
        parse_category(cat,planet,jsfile,cname,planet) 

def parse_category(cat, planet_name, jsfile, cname,pname):
    if cat=="Space" and len(planet_name)==0:
        parse_space(cat,jsfile,cname)
        return
    t=open(folder+jsfile,"r")
    s=t.read()
    t.close()
    p=esprima.parseScript(s)
    planet_label_en=""

    building_class=None
    for dojo_declare in p.body:
        if dojo_declare.expression.arguments[0].value==cname:
            building_class=dojo_declare.expression.arguments[2]
            break

    buildings_data=None
    for prop in building_class.properties:
        #print(prop.key.name)
        if prop.key.name==pname:
            buildings_data=prop

    if buildings_data==None:#this is probably due to space
        planets_property=find_property(building_class,"planets")
        planets_list=planets_property.value.elements
        for planet in planets_list:
            if get_property_value(planet,"name")==pname:
                buildings_data=find_property(planet,"buildings")
                planet_label_en=get_label(find_property(planet,"label").value.arguments[0].value)
                break

    buildings_list=buildings_data.value.elements

    for b in buildings_list:
        ratio=get_property_value(b,"priceRatio")
        if cat=="Trade":
            ratio=1.15
        if cat=="Buildings":
            name_property=find_property(b,"name")
            name=name_property.value.value
        else:
            name=""
        if find_property(b,"stages")==None:
            upgradable=False
            label_property=find_property(b,"label")
            if label_property==None:
                label_property=find_property(b,"title")
            label=label_property.value.arguments[0].value
            if cat=="Trade" and label=="trade.race.leviathans":
                continue#no embassy for leviathans
        else:
            upgradable=True
            label=""
        if(upgradable):
            stages=find_property(b,"stages")
            for i in range(len(stages.value.elements)):
                s=stages.value.elements[i]
                label=find_property(s,"label").value.arguments[0].value
                ratio_u=get_property_value(s,"priceRatio")
                if(ratio_u=="NotFound"):
                    ratio_u=ratio
                label_en=get_label(label)
                kg_db.append([cat,planet_label_en,label_en,i+1,ratio_u,get_materials(s),name])

        else:
            label_en=get_label(label)
            kg_db.append([cat,planet_label_en,label_en,upgradable,ratio,get_materials(b),name])

categories=[
    ["Trade","","diplomacy.js","classes.managers.DiplomacyManager","races"],
    ["Buildings","","buildings.js","classes.managers.BuildingsManager","buildingsData"],
    ["Ziggurats","","religion.js","classes.managers.ReligionManager","zigguratUpgrades"],
    ["Order of the Sun","","religion.js","classes.managers.ReligionManager","religionUpgrades"],
    ["Cryptotheology","","religion.js","classes.managers.ReligionManager","transcendenceUpgrades"],
    ["Pacts","","religion.js","classes.religion.pactsManager","pacts"],
    ["Chronoforge","","time.js","classes.managers.TimeManager","chronoforgeUpgrades"],
    ["Void","","time.js","classes.managers.TimeManager","voidspaceUpgrades"],
    ["Space","","space.js","classes.managers.SpaceManager",""]
    ]

def insert_into_db(db_cursor,b):
    db_cursor.execute('''
    INSERT INTO BUILDINGS
    (Category,Planet,Name,Upgradable,Ratio,GroupName,Recipe)
    VALUES(?,?,?,?,?,?,?)''',
    (b[0],b[1],b[2],b[3],0 if b[4]=="NotFound" else b[4],get_group_name(b[6]),str(b[5])))


def parse_db(s):
    global log
    log=c.newwin(17,70,6,5)
    db_link=sl.connect(KG_DB_FILE)
    db_link.row_factory = sl.Row
    db_cursor=db_link.cursor()
    db_cursor.execute('''CREATE TABLE IF NOT EXISTS BUILDINGS
    (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Category TEXT,
        Planet TEXT,
        Name TEXT,
        Upgradable INTEGER,
        Ratio REAL,
        GroupName TEXT,
        Recipe TEXT
    )''')

    get_groups()
    for cat in categories:
        if len(cat[1])==0:
            log.addstr("Parsing "+cat[0]+"...\n")
        else:
            log.addstr("Parsing "+cat[1]+"...\n")
        log.refresh()
        parse_category(cat[0],cat[1],cat[2],cat[3],cat[4])

    db_cursor.execute("DELETE FROM BUILDINGS")
    for b in kg_db:
        if b[0]!="Buildings":
            insert_into_db(db_cursor,b)
    #buildings must be ordered according to groups
    for g in groups_contents:
        for b_name in g:
            for b in kg_db:
                if b[6]==b_name:
                    insert_into_db(db_cursor,b)


    db_link.commit()
    db_link.close()

    log.addstr("<END>")


def show(s):
    fill=' '*(PATH_WIDTH-len(folder))
    test_udr=pure_math.get_unlimited_dr(test_value,test_stripe)
    test_ldr=pure_math.get_limited_dr(test_effect,test_limit)
    s.addstr(2,COL_D_0,"DEBUG PAGE. DO NOT USE.",c.color_pair(HELP_BOLD))
    s.addstr(4,COL_D_0,"A: Run tests")
    s.addstr(5,COL_D_0,"B: Folder with KG sources:")
    s.addstr(6,COL_D_0,folder+fill,c.color_pair(OTHER_BTN))
    s.addstr(7,COL_D_0,"C: Rebuild database (old one will be preserved)")
    s.addstr(9,COL_D_0,"D: Test keys")
    s.addstr(11,COL_D_0,f"Unlimited DR Test: {test_udr}")
    fill=' '*(EDIT_WIDTH-len(str(test_value)))
    s.addstr(12,COL_D_0,"E: Value:")
    s.addstr(12,COL_D_1,f"{test_value}"+fill,c.color_pair(OTHER_BTN))
    fill=' '*(EDIT_WIDTH-len(str(test_stripe)))
    s.addstr(13,COL_D_0,"F: Stripe:")
    s.addstr(13,COL_D_1,f"{test_stripe}"+fill,c.color_pair(OTHER_BTN))
    s.addstr(15,COL_D_0,f"Limited DR Test: {test_ldr}")
    fill=' '*(EDIT_WIDTH-len(str(test_effect)))
    s.addstr(16,COL_D_0,"G: Effect:")
    s.addstr(16,COL_D_1,f"{test_effect}"+fill,c.color_pair(OTHER_BTN))
    fill=' '*(EDIT_WIDTH-len(str(test_limit)))
    s.addstr(17,COL_D_0,"H: Limit:")
    s.addstr(17,COL_D_1,f"{test_limit}"+fill,c.color_pair(OTHER_BTN))



    if esprima_absent:
        s.addstr(8,COL_D_0,"WARNING! esprima package is absent! No parsing available.",c.color_pair(ATTENTION))

def react(s,ch,m,alt_ch):
    global folder
    global test_value
    global test_stripe
    global test_effect
    global test_limit
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

    if letter=="A":
        return M_HIDDEN_TEST
    if letter=="B":
        tabs.active=M_EDIT
        tabs.show_footer(s)
        tabs.active=M_WORKSHOP
        s.keypad(1)
        s.refresh()
        c.curs_set(1)
        win = c.newwin(1,PATH_WIDTH,6, 11)
        tb = c.textpad.Textbox(win)
        text = tb.edit(utils.edit_keys)
        c.curs_set(0)
        del win
        if utils.user_cancel:
            utils.user_cancel=False
        else:
            t_stripped=text.strip()
            if t_stripped.endswith("js/") or t_stripped.endswith("js\\") or t_stripped.endswith("js"):
                folder=text.strip()+"/"
            else:
                folder=text.strip()+"/js/"
    if ch==27:
        return M_BONFIRE
    if letter=="C":
        if esprima_absent:
            utils.show_message("Install esprima python package!")
            return M_BONFIRE
        if len(folder)<5:
            utils.show_message("Folder must contain '/js/' subfolder.")
            return M_BONFIRE
        if os.path.exists(folder+"buildings.js")==False:
            utils.show_message("No KG sources found!")
            return M_BONFIRE
        num=0
        while True:
            old_file=KG_DB_FILE+f".{num}.old"
            if os.path.exists(old_file):
                num+=1
                continue
            os.rename(KG_DB_FILE,old_file)
            break
        parse_db(s)
        utils.show_message("Parse completed. Please restart.")
        return M_BONFIRE
    if letter=="D":
        s.clear()
        s.addstr("TESTING KEYS. ^Q TO EXIT.\n")
        while True:
            ch=s.getch()
            st=c.keyname(ch).decode("utf8")
            s.addstr("KEY:"+st+"|")
            if st=="KEY_MOUSE":
                m=c.getmouse()
                s.addstr(f"MOUSE:0[{m[0]}],1[{m[1]}],2[{m[2]}],3[{m[3]}],4[{m[4]}]|")
            if st=="^Q":
                return M_DATABASE

    if letter=="E":
        text=utils.textpad(s,12,COL_D_1,EDIT_WIDTH)
        if len(text)>0:
            try:
                val=pure_math.parse_num(text.strip())
            except:
                utils.show_message("Invalid input!")
                val=0
            test_value=val
    if letter=="F":
        text=utils.textpad(s,13,COL_D_1,EDIT_WIDTH)
        if len(text)>0:
            try:
                val=pure_math.parse_num(text.strip())
            except:
                utils.show_message("Invalid input!")
                val=0
            test_stripe=val
    if letter=="G":
        text=utils.textpad(s,16,COL_D_1,EDIT_WIDTH)
        if len(text)>0:
            try:
                val=pure_math.parse_num(text.strip())
            except:
                utils.show_message("Invalid input!")
                val=0
            test_effect=val
    if letter=="H":
        text=utils.textpad(s,17,COL_D_1,EDIT_WIDTH)
        if len(text)>0:
            try:
                val=pure_math.parse_num(text.strip())
            except:
                utils.show_message("Invalid input!")
                val=0
            test_limit=val


    return M_DATABASE