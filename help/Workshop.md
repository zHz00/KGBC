This screen enables you to switch different discounts
available in Kittens Game. Only options affecting
buildings' prices are present.

Settings are saved in kgbc\_settings.txt file every time
user changes an option.

#=== KEYS ===
F1           Show help
F10          Exit
Letters      Select discount type
Esc          Return to Bonfire

Using letters R, S, T (for _burned paragon_, _elevators_ and
_1000 years challenge_) will bring you to editing field.

#=== MOUSE ===

Click in brackets to activate discount. Click on the
edit box to begin editing.

#=== THEORY. DISCOUNT TYPES ===

All discounts are divided into two categories: ratio
discounts and base discounts.

*Ratio discounts* influence the multiplier of next
building.

**Example.**

First _Library_ costs 25 wood and has a ratio of 1.15.

The common formula for this scenario is:

#Nth=Base\*Ratio^(N-1)

So, the 10th _Library_ costs 25\*1.15^9=87.947 wood.

If you have ratio discount, for example, _Enlightenment_,
your ratio will be lesser, but base cost is unmodified.

_Enlightenment_ gives you 1% discount, so ratio will be
1.15-0.01=1.14. 

So, 10th _Library_ will cost 25\*1.14^9=81.299.

*Base discounts* affect base cost, leaving the ratio the
same.

**Example.**

_Fascism_ policy gives you -50% base discount to _Log_
_House_.

Default base price of _Log House_ is 200 wood and 250
minerals.

Prices are:

N     wood    minerals
1     200.0   250.0
...
10    703.575 879.469

If you activate _Fascism_, prices will be:

N     wood    minerals
1     100.0   125.0
...
10    351.788 439.735

Both types of discounts can be combined. In this case 
base price is reduced first, then it is multiplied
by reduced price ratio.

#=== THEORY. DIMINISHING RETURNS ===

The game has two types of diminishing returns: limited
and unlimited.

If the effect has *limited DR*, then you receive 75% of
the effect linearly, but last 25% will be diminished
with something like 1/x.

Exact formula is:

#       /effect, if |effect| < u
#       |
#Result=|
#       |                d
#       \\u+d\*(1- ----------------)
#                |effect| - u + d

where d=0.25\*limit and u=0.75\*limit

**Example.**

Let's talk about _Space Elevators_.

_Elevators_ affect oil base cost of space buildings.
Maximum discount you can get is -75%, but it is subject
of *Limited Diminishing Returns*. So you get undiminished
returns as usual till 75% of effect, which means 75% of
-75%, which is 0.75\*-0.75%=-56.25%.

Every _elevator_ gives you -5% discount. Let's calculate
discount for 20 elevators.

20\*-5%=-100%, which is greater (in absolute value) than 
-56.25%. So let's try *Limited DR* formula.

#d=0.25\*limit=0.25\*0.75=0.1875
#u=0.75\*limit=0.75\*0.75=0.5625

#                               0.1875
#result=0.5625+0.1875\*(1- ------------------)=0.69375.
#                         1.00-0.5625+0.1875

So final base discount for oil will be -69.38%.

*Unlimited DR* is used, for example, when calculating
_Burned Paragon_ effect.

This formula has no strict limit, but progresses slower
and slower. It is like square root. Exact formula is:

#effect=(sqrt(1 + (value / stripe) \* 8) - 1) / 2

Stripe regulates steepness of curve and it is given in
every case.

**Example.**

Let's count _Burned Paragon_ effect for _Philosopher leader_.

From the source code we know, that stripe value for this
effect is equal to 500 (see getBurnedParagonRatio()
function in prestige.js).

So, if we have zero _Burned Paragon_, effect will be:

#effect=(sqrt(1+(0/500)\*8)-1)/2=0

And if we have 10K of _Burned Paragon_, effect will be:

#effect=(sqrt(1+(10000/500)\*8)-1)/2=5.844

This effect is used as a multiplier for bonus, so we
need to add 1.0 to make default effect with zero _Burned_
_Paragon_:

#BP Ratio=1.0+effect=1.0 (0 BP)
#BP Ratio=1.0+effect=6.844 (10K BP)

Unfortunately, _Philosopher leader_ receives only 10% of
this bonus. So the discount multiplier will be:

#BP ratio 10%=(0.9+0.1\*BP ratio)=1.58

This is multiplied by the default _Philosopher_ discount
which is equal to 10%.

So the final discount is -10%\*1.58=-15.8%

#=== GROUPS OF DISCOUNTS IN WORKSHOP TAB ===

*1. Metaphysics*

These discounts affect only buildings in the **Bonfire**
tab.

Discounts affect price ratio, not the base price. So
first building will have same price as usual, but next
building will be cheaper.

Discounts are simply subtracted from default ratio one
by one. If you selected some discount, you also get all
previous discounts.

**Example:**

You have selected _Golden Ratio_ and want to build a
_Quarry_.
Default ratio is 1.15.
_Enlighenment_ gives you -1% discount.
_Golden Ratio_ gives you an additional -1.618%.

Total discount is -2.618% and final ratio is:
#1.15-0.02618=1.124.

Please note that _Metaphysics_ discounts are affected by
*Limited Diminishing Returns*. If your discount is more
than 75% of (ratio-1.0), then you get only part of
discount.

**Example:**

You have selected _Renaissance_ and want to build an
_Observatory_.

Default ratio is 1.10.
All discounts gives you a total of -8.686%.

It seems that final ratio is 1.15-0.08686=1.01314.

But it isn't, because 75% of (1.10-1.0) is 0.075=7.5%.

So discounts that are greater than -7.5% are subject to
*Limited Diminishing Returns*.

You'll get the ratio of 1.017 instead of 1.01314.

*2. Huts*

Huts discounts affect ratio. They are subtracted from
the default ratio of 2.5. Similar to _Metaphysics_
discounts, selecting any discount gives you all
previous discounts.

**Example:**

You have selected _Concrete huts_, which means you get
_Ironwoods huts_ AND _Concrete huts_ discounts.

_Ironwoods huts_ gives you -50% to ratio.
_Concrete huts_ gives you -30% to ratio.
Default ratio is 2.5.

Final ratio is 2.5-0.5-0.3=1.7

Please note that _Huts_ discount is also a subject to
*Limited Diminishing Returns* with same rules as in
previous exapmles.

**Example.**

_Huts_ default ratio is 2.5. So 2.5-1.0=1.5
75% of 1.5 is 1.125, which means that discount more
than -112.5% will be reduced.

You have selected _Vitruvian Feline_ for total of -6.396%
and selected _Eludium huts_ (-115% in total).

Undiminished discount will be -115%-6.396%=-121.396%.
This is greater (in absolute value) than -112.5%.

Undiminished ratio will be 1.28604, but diminished ratio
will be 1.303.

*3. Policies*

Policies affect base price, not ratio. So while your
ratio will be the same, first building will be cheaper.
Of course, subsequent buildings also will be cheaper,
but this is due to base cost reduction.

**Liberalism** affects only gold cost, but all building on
all tabs are affected. This includes _Mint_, _Tradepost_
and _Temple_ on **Bonfire** tab, _Ziggurats_ and _Order of the_
_Sun_. Discount is equal to -20% of base price.

**Fascism** affects _Log House_ base cost. Discount is
-50%. This means that you can build 5 additional _Log_
_Houses_ until you reach the cap (with default ratio).

**Communism** gives you -30% to _Factory_ base cost. This is
approximately 3 additional _Factories_ until the cap with
default ratio.

**Big Stick Policy** affects all _Embassies_ and reduce base
cost by -15%. No other discounts for _Embassies_ are
available. This discount gives you 1-2 additional
_Embassies_ until the cap.

*4. Other*

_Philosopher leader_, _Monarchy_ policy and amount of
_Burned paragon_ make _Order of the Sun_ upgrades cheaper.
They all affect base prices.

_Philosopher leader_ is essential. Otherwise you don't
receive any discount.

Philosopher leader              -10% base discount
Monarchy+Philosopher leader     -19.5% base discount
Adding burned paragon           up to -100%

_Burned paragon_ effect uses *Unlimited Diminishing*
*Returns* formula. It is quite slow.

**Examples:**

You have _Philosopher leader_ and _Monarchy_. Effects are:

Burned paragon        Effect
0                     -19.5%
1000                  -22.55%
10K                   -30.9%
100K                  -57.54%
1M                    -93.2%

Discount got via _Liberalism_ policy is applied
multiplicatively.

**Example.**

You have _Philosopher leader_ and _Liberalism_.
Faith multiplier will be 0.9, because of 10% discount.
Gold multiplier will be 0.9\*0.8=0.72, because 20% base
cost discount means 0.8 multiplier and 10% means 0.9
multiplier.

So final base discount of gold will be -28%.

Please note that after all discounts *Limited*
*Diminishing Returns* is applied.

The number of _Elevators_ affects oil needed for space
buildings.

These include: _Satellite_, _Space St._, _Lunar Outpost_ and
_Moon Base_.

_Elevators_ affect base oil cost of these buildings up
to the maximum  of -75%, but this is subject to *Limited*
*Diminishing Returns*. So you get undiminished
returns as usual till 75% of effect, which means 75% of
-75%, which is -56.25%.

Every elevator gives you -5% discount to base oil cost,
so first 11 elevators effect will be undiminished.

**Examples:**

Elevators     Effect
1             -5%
10            -50%
15            -65.62%
20            -69.38%
100           -74.24%

_1000 years challenges_ affect only _Temporal Press_ from
**Time** tab.

Every completion of this challenge gives you -0.1% ratio
discount but not more than -9% in total. You receive
discount linearly without any Diminishing Returns
formula, but 90th completion is the last.

**Example.**

Completions       Final ratio
0                 1.1 (unavailable)
1                 1.099
10                1.09
50                1.05
90                1.01
91                1.01
1000              1.01

<END>