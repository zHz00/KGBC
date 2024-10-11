from pure_math import get_limited_dr
from pure_math import get_unlimited_dr
import copy

from constants import *

global_list=["(None)","Enlighenment","Golden Ratio","Divine Proporion","Vitruvian Feline","Renaissance"]
global_values=[0,-1.000,-2.618033988749895,-4.395811766527673,-6.395811766527673,-8.645811766527673]
global_idx=0

huts_list=["(None)","Ironwood","Concrete","Unobtanium","Eludium"]
huts_values=[0,-50,-80,-105,-115]
huts_idx=0

policies_list=["Liberalism","Fascism","Communism","Big Stick Policy"]
policies_list_short=["Lib","Fas","Comm","B. Stick"]
policies_desc=["-20% gold base prices","-50% log house base price","-30% factory base price","-15% embassy base price"]
policies_active=[0,0,0,0]

philosofer=0
monrachy=0
bparagon=0
elevators=0
challenge_1k=0

space_oil_list=["Satellite","Space St.","Lunar Outpost","Moon Base"]

def using_oil_ratio(b):
    if b["Name"] in space_oil_list:
        return True
    return False

def using_starchart_ratio(b):
    if b["Name"] == "Spaceport":
        return True
    return False

def get_philosopher_mul():
    mul=1.0
    discount=0.0
    if philosofer==0:
        return 1.0
    if philosofer==1:
        discount=0.1
    if monrachy==1:
        discount=0.195
        
    bparagon_ratio=1+get_unlimited_dr(bparagon,500)
    discount*=(0.9+0.1*bparagon_ratio)
    discount=get_limited_dr(discount,1.0)
    mul=1.0-discount
    return mul

def get_space_oil_mul():
    mul=1-(get_limited_dr(5*elevators,75)/100)
    return mul

def get_temporal_press_discount():
    if challenge_1k<=90:
        discount=-0.001*challenge_1k
        return discount
    return -0.09

def get_discount(b):
    if b["Name"]=="Hut":
        total_discount=global_values[global_idx]+huts_values[huts_idx]
        total_discount=get_limited_dr(total_discount/100,b["Ratio"]-1)
        return total_discount
    if b["Category"]=="Buildings":
        discount=global_values[global_idx]/100.0
        discount_dr=get_limited_dr(discount,b["Ratio"]-1)
        return discount_dr
    if b["Name"]=="Temporal Press":
        return get_temporal_press_discount()
    return 0

def base_discount(b):
    mul=1.0
    mul_gold=1.0
    mul_oil=1.0
    if b["Name"]=="Log House" and policies_active[1]==1:#fascism
        mul=0.5
    if b["Name"]=="Factory" and policies_active[2]==1:#communism
        mul=0.7
    if "gold" in b["Recipe"].keys() and policies_active[0]==1:#liberalism
        mul_gold=0.8
    if b["Name"] in space_oil_list and elevators>0:
        mul_oil=get_space_oil_mul()
    if b["Category"]=="Trade" and policies_active[3]==1:#big stick policy
        mul=0.85
    if b["Category"]=="Order of the Sun":
        mul=get_philosopher_mul()

    b_reduced=copy.deepcopy(b)
    for mat in b_reduced["Recipe"]:
        if mat=="gold":
            b_reduced["Recipe"][mat]*=mul_gold
        if mat=="oil":
            b_reduced["Recipe"][mat]*=mul_oil
        b_reduced["Recipe"][mat]*=mul
    return (b_reduced["Recipe"],mul,mul_gold,mul_oil)

if __name__=="__main__":
    print("Not main module! ("+__file__+")")