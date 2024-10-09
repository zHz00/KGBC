import esprima
import json
import sqlite3 as sl
folder="E:\\ex\\kittensgame-src\\kittensgame-master\\js\\"

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

def print_space():
    planet_names=get_planet_list()
    for planet in planet_names:
        print(f"=== PLANET:{planet} ===")
        print_category("space.js","classes.managers.SpaceManager",planet)


def print_category(jsfile, cname,pname):
    t=open(folder+jsfile,"r")
    s=t.read()
    t.close()
    p=esprima.parseScript(s)
    #print(type(p))
    #p0=p.body[0]
    #ea2=p0.expression.arguments[2]
    #print(type(p0))
    #print(type(ea2))

    building_class=None
    for dojo_declare in p.body:
        if dojo_declare.expression.arguments[0].value==cname:
            building_class=dojo_declare.expression.arguments[2]

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

    buildings_list=buildings_data.value.elements

    for b in buildings_list:
        ratio=get_property_value(b,"priceRatio")
        if find_property(b,"stages")==None:
            upgradeble=False
            name=find_property(b,"label").value.arguments[0].value
        else:
            upgradeble=True
            name=""
        if(upgradeble):
            print(f"Name: {name}, Upgradeble!")
            stages=find_property(b,"stages")
            for s in stages.value.elements:
                name=find_property(s,"label").value.arguments[0].value
                ratio_u=get_property_value(s,"priceRatio")
                if(ratio_u=="NotFound"):
                    ratio_u=ratio
                print(f"=== Name: {name}, Ratio:{ratio_u}")
                print("===",get_materials(s))

        else:
            print(f"Name: {name}, Ratio:{ratio}")
            print(get_materials(b))

kg_db=[]

def parse_space(cat,jsfile,cname):
    planet_names=get_planet_list()
    for planet in planet_names:
        print("Parsing "+planet+"...")
        parse_category(cat,planet,jsfile,cname,planet) 

def parse_category(cat, planet_name, jsfile, cname,pname):
    if cat=="Space" and len(planet_name)==0:
        parse_space(cat,jsfile,cname)
        return
    t=open(folder+jsfile,"r")
    s=t.read()
    t.close()
    p=esprima.parseScript(s)
    planet_name_en=""

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
                planet_name_en=get_label(find_property(planet,"label").value.arguments[0].value)
                break

    buildings_list=buildings_data.value.elements

    for b in buildings_list:
        ratio=get_property_value(b,"priceRatio")
        if cat=="Trade":
            ratio=1.15
        if find_property(b,"stages")==None:
            upgradable=False
            name_property=find_property(b,"label")
            if name_property==None:
                name_property=find_property(b,"title")
            name=name_property.value.arguments[0].value
            if cat=="Trade" and name=="trade.race.leviathans":
                continue#no embassy for leviathans
        else:
            upgradable=True
            name=""
        if(upgradable):
            stages=find_property(b,"stages")
            for i in range(len(stages.value.elements)):
                s=stages.value.elements[i]
                name=find_property(s,"label").value.arguments[0].value
                ratio_u=get_property_value(s,"priceRatio")
                if(ratio_u=="NotFound"):
                    ratio_u=ratio
                name_en=get_label(name)
                kg_db.append([cat,planet_name_en,name_en,i+1,ratio_u,get_materials(s)])

        else:
            name_en=get_label(name)
            kg_db.append([cat,planet_name_en,name_en,upgradable,ratio,get_materials(b)])

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

#print_category("buildings.js","classes.managers.BuildingsManager","buildingsData")
#print_category("religion.js","classes.managers.ReligionManager","zigguratUpgrades")
#print_category("religion.js","classes.managers.ReligionManager","religionUpgrades")
#print_category("religion.js","classes.managers.ReligionManager","transcendenceUpgrades")
#print_category("religion.js","classes.religion.pactsManager","pacts")
#print_category("time.js","classes.managers.TimeManager","chronoforgeUpgrades")
#print_category("time.js","classes.managers.TimeManager","voidspaceUpgrades")
#print_category("space.js","classes.managers.SpaceManager","cath")
#print_space()
for c in categories:
    if len(c[1])==0:
        print("Parsing "+c[0]+"...")
    else:
        print("Parsing "+c[1]+"...")
    parse_category(c[0],c[1],c[2],c[3],c[4])

print("Categories:")
for i in range(len(categories)):
    print(f"{i}. {categories[i][0]}")
#selected_cat=int(input("Select category:"))
#for b in kg_db:
    #if b[0]==categories[selected_cat][0]:
        #print(b)
db_link=sl.connect("kg_db.db")
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
        Recipe TEXT
    )''')
db_cursor.execute("DELETE FROM BUILDINGS")
for b in kg_db:
    db_cursor.execute('''
    INSERT INTO BUILDINGS (Category,Planet,Name,Upgradable,Ratio,Recipe) VALUES(?,?,?,?,?,?)''',(b[0],b[1],b[2],b[3],0 if b[4]=="NotFound" else b[4],str(b[5])))
db_link.commit()
db_link.close()

print("end")
