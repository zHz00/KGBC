import math

from constants import *

postfix_list=["","K","M","G","T","P","E","Z","Y","R","Q"]

def get_limited_dr(effect,limit):
    if abs(effect)<0.75*limit:
        return effect
    d=0.25*limit
    u=0.75*limit

    try:
        effect_dr=u+d*(1-d/(abs(effect)-u+d))
    except:
        return math.nan
    if effect>0:
        return effect_dr
    else:
        return -effect_dr


def get_unlimited_dr(value, stripe):
    try:
        result = (math.sqrt(1 + (value / stripe) * 8) - 1) / 2
    except:
        try:
            result= math.sqrt(value) / math.sqrt(stripe) * math.sqrt(2)
        except:
            result=math.nan
    return result

def format_num(real:float,mode,fill=True) -> str:
    if real<=0:
        return str(real)#we don't need negatives, but zero must be correct
    value_str=""
    idx=-1
    try:
        idx=int(math.log10(real)//3)
    except ValueError:
        value_str="[NaN]"
    if idx!=-1:
        if idx>=len(postfix_list) or mode==FLOAT_SCI:
            value_str=("%.4e"%real)
        else:
            value_str=("%.3f"%(real/(10**(idx*3))))+postfix_list[idx]
    if fill==True:
        value_str+=" "*(COL_WIDTH-len(value_str)-1)
    return value_str

def parse_num(s:str)->float:
    val=0.0
    try:
        val=float(s)
    except:
        postfix=s[-1].capitalize()
        if postfix in postfix_list:
            ex=postfix_list.index(postfix)*3
            s_num=s[:-1]#delete last character
            val=float(s_num)*(10**ex)#this may be exception, this is normal, it'll be caught one level upper
        else:
            raise ValueError
    return val

if __name__=="__main__":
    print("Not main module! ("+__file__+")")