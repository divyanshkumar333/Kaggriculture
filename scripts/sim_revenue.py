import math

def get_price(item, inv):
    I0 = 10000
    if item == "MELON":
        base, T, below_f, below_t, above_f, above_t = 250, 300, "log", 0.20, "sq", 3.60
    elif item == "STRAWBERRY":
        base, T, below_f, below_t, above_f, above_t = 120, 100, "sqrt", 0.70, "linear", 1.60
    elif item == "MILK":
        base, T, below_f, below_t, above_f, above_t = 160, 122, "sqrt", 0.60, "linear", 1.60
    elif item == "WOOL":
        base, T, below_f, below_t, above_f, above_t = 200, 105, "log", 0.20, "sq", 3.20
    else:
        return 1
        
    diff = abs(inv - I0)
    sign = 1 if inv < I0 else -1
    f_str = below_f if inv < I0 else above_f
    t_val = below_t if inv < I0 else above_t
    
    u = diff / T
    if f_str == "linear": f = u
    elif f_str == "sq": f = u**2
    elif f_str == "sqrt": f = math.sqrt(u)
    elif f_str == "log": f = math.log(1 + u)
    else: f = u
    
    amp = t_val * base
    price = base + sign * amp * f
    return max(1, round(price))

def simulate_revenue():
    inv = {"MELON": 10000, "STRAWBERRY": 10000, "MILK": 10000, "WOOL": 10000}
    cash = 0
    
    for day in range(20):
        # Extreme favorable town shops
        inv["MELON"] -= 1  
        inv["STRAWBERRY"] -= 50 # massive strawberry demand
        inv["MILK"] -= 40 # massive milk demand
        inv["WOOL"] -= 25 # massive wool demand
        
        # Sell Melon
        for _ in range(19):
            p = get_price("MELON", inv["MELON"])
            cash += p
            if p > 1: inv["MELON"] += 1
        for _ in range(12):
            if get_price("MELON", inv["MELON"]) > 1: inv["MELON"] += 1
            
        # Sell Strawberry
        for _ in range(72):
            p = get_price("STRAWBERRY", inv["STRAWBERRY"])
            cash += p
            if p > 1: inv["STRAWBERRY"] += 1
        for _ in range(66):
            if get_price("STRAWBERRY", inv["STRAWBERRY"]) > 1: inv["STRAWBERRY"] += 1
            
        # Sell Milk
        for _ in range(9):
            p = get_price("MILK", inv["MILK"])
            cash += p
            if p > 1: inv["MILK"] += 1
        for _ in range(9):
            if get_price("MILK", inv["MILK"]) > 1: inv["MILK"] += 1
            
        # Sell Wool
        for _ in range(4):
            p = get_price("WOOL", inv["WOOL"])
            cash += p
            if p > 1: inv["WOOL"] += 1
        for _ in range(5):
            if get_price("WOOL", inv["WOOL"]) > 1: inv["WOOL"] += 1
            
    print(f"Total theoretical cash with favorable town: {cash}")

simulate_revenue()
