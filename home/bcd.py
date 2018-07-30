def bcd2dec (val):
    dizaine = (val >> 4) * 10
    unite = val & 0x0F
    print dizaine, unite
    return (dizaine+unite)

print bcd2dec (6)
print bcd2dec (0b00010001)
