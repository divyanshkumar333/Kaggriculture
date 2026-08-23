# Kaggriculture Economic Model

This document outlines the exact market-pricing mechanics verified directly from the `kaggriculture` environment source code (`kaggriculture.py`).

## VERIFIED FROM ENVIRONMENT

### Core Price Function
The price of any product is calculated dynamically based on the current market `inventory` compared to the initial inventory `I0` (10,000).

```python
def _shape(func, x, T=None):
    x = max(0.0, x)
    if func == "linear": return x
    if func == "sq":     return x * x
    if func == "sqrt":   return math.sqrt(x)
    if func == "log":    return math.log(1.0 + x)
    if func == "hinge":
        if not T or T <= 0:
            return x
        u = x / T
        return u + 8.0 * max(0.0, u - 1.0) ** 2
    return x

def market_price(item, inventory, params):
    base = p["base"]
    I0 = p["I0"]
    T = p["T"]
    if inventory < I0:
        f = p["below_func"]
        amp = p["below_target"] * base / _shape(f, T, T)
        price = base + amp * _shape(f, I0 - inventory, T)
    else:
        f = p["above_func"]
        amp = p["above_target"] * base / _shape(f, T, T)
        price = base - amp * _shape(f, inventory - I0, T)
    
    return max(1, int(round(price)))
```

### Exact Parameters Discovered

| Resource | Base | I0 | T | Below func | Below target | Above func | Above target |
| ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- |
| **WHEAT** | 25 | 10000 | 400 | sqrt | 0.80 | log | 0.20 |
| **CARROT** | 35 | 10000 | 450 | hinge | 1.00 | sqrt | 0.70 |
| **TOMATO** | 60 | 10000 | 200 | hinge | 0.40 | sqrt | 0.60 |
| **STRAWBERRY** | 120 | 10000 | 100 | sqrt | 0.70 | linear | 1.60 |
| **MELON** | 250 | 10000 | 300 | log | 0.20 | sq | 3.60 |
| **EGG** | 50 | 10000 | 332 | hinge | 0.40 | log | 0.20 |
| **MILK** | 160 | 10000 | 122 | sqrt | 0.60 | linear | 1.60 |
| **WOOL** | 200 | 10000 | 105 | log | 0.20 | sq | 3.20 |
| **FERTILIZER** | 100 | 10000 | 200 | linear | 0.40 | linear | 0.40 |

### Order Processing Behavior (Sell Order Simulation)
* The market accepts up to `maxMarketOrdersPerTurn` (default 10) orders per player.
* Orders are processed unit-by-unit concurrently. For a single agent operating alone, a sell order of `N` units behaves as a loop:
  1. Determine `price = market_price(inventory)`
  2. Revenue increases by `price`
  3. If `price > 1`, `inventory` increases by 1.
  4. If `price == 1` (the `PRICE_FLOOR`), the item is sold for $1 but **is NOT added to the market inventory**, preventing the inventory from infinitely inflating.

### Exact Functions
* **linear**: $f(x) = x$
* **sq**: $f(x) = x^2$
* **sqrt**: $f(x) = \sqrt{x}$
* **log**: $f(x) = \ln(1 + x)$
* **hinge**: $f(x) = \frac{x}{T} + 8 \cdot \max(0, \frac{x}{T} - 1)^2$
* **Rounding Behavior**: Values are explicitly rounded with `int(round(price))` and floored at `1` (`PRICE_FLOOR`).

## INFERENCE / HYPOTHESIS

* **Opponent Interference**: Because orders are processed concurrently unit-by-unit, selling exactly the same product on exactly the same turn as an opponent will cause the price to drop twice as fast per unit sold.
* **Bulk Selling**: Selling 10 units in one turn incurs exactly the same price impact as selling 1 unit over 10 turns, assuming no opponent interference and no town shop consumption during those turns. Therefore, the decision to trickle-sell vs bulk-sell should be driven by worker action efficiency and shed capacity, rather than price impact.
