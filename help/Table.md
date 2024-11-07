This tab shows prices of the selected building. You can
view prices for any number of buildings until overflow
(~1.7e308).

#=== KEYS ===

F1           Show help
F10          Exit
Esc          Return to previous tab

Up           Move cursor one line up
Down         Move cursor one line down
Page Up      Move cursor one screen up (-20)
Page Down    Move cursor one screen down (+20)
Home         To the beginning
End          Move cursor down +100 buildings

[ and ]      Begin/finish selection.
Ins          Far Manager-style selection (works weird)
- or Gray -  Remove selection
Tab          Switch between scientific and KG format


Hidden features:
+            Add building at cursor to test list
S            Save tests to kgbc\_tests.txt


#=== MOUSE ===

Right click              Back
Click on right arrow     Back
Click on table           Move cursor
Mouse wheel              Scroll table
Double/Middle click      Begin/finish selection
Click on header          Remove selection

#=== INFORMATION ===

*Price ratio and discount information.*

All discounts information on other screens are just
hints. Real discounts information for every building is
displayed on this screen in second line.

**LEFT caption** shows ratio for building. If it is lesser
than default ratio, then default ratio is shown in
parenthesis. If some resource have separate ratio, this
is also shown.

**RIGHT caption** can be absent. This means there is no
discount. If it is present, it shows base price
discount for all resources or for some specific.

*Selection.*

When you use selection, you can see sum of selected
buildings in bottom line. This can help you to estimate
amount of resources needed to build desired number of
additional buildings.

*[ and ] working details.*

These keys works similarly and there is no difference
between them. First key pressed begins selection. After
that you can move cursor as usual and you will see sum
of selected buildings, but final line of selection will
move together with cursor. If you want to move cursor
separately, you must end selection with either [ or ]
key.

*Ins working details*

Ins can be used to edit existing (finished) selection.

-- If there is no selection, Ins makes one-line
selection and moves cursor down.
-- If the cursor is **immediately after** last line of
selection, selection is extended by one line, and cursor
moves down.
-- If the cursor is **immediately before** first line of
selection, selection is extended by one line, but the
cursor remains on place.
-- If the cursor is **at the first line of selection**, then
selection is reduced by one line and cursor moves one
line down, allowing you to reduce selection further.
-- If the  cursor is **at the last line of selection**, then
selection is reduced by one line, but the cursor remains
intact. In this case you must move cursor manually.
-- In other cases Ins key is ignored.

*Asterisk in first column.*

Sometimes you see strange asterisk near number of
buildings in first column. This means that buying
indicated number of buildings will give you a new color
scheme (in original KG, not in KGBC!).
<END>